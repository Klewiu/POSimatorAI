from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from .form import EstimationForm
from .models import EstimationInput
from ml.predict import predict_price
from django.views.generic import TemplateView
from apps.submits.models import Submission
from ml.predict import MODEL  # importujemy model z predict.py
from google import genai
from google.genai import types


class EstimationView(LoginRequiredMixin, FormView):
    template_name = "estimations/form.html"
    form_class = EstimationForm
    success_url = "/estimations/result/"

    def get_initial(self):
        initial = super().get_initial()
        for field_name in self.form_class.base_fields:
            value = self.request.GET.get(field_name)
            if value not in (None, ""):
                initial[field_name] = value
        return initial

    def form_valid(self, form):
        input_data = form.save()

        # Wywołanie predykcji
        predicted_result = predict_price({
            "naklad_szt": input_data.naklad_szt,
            "objetosc_m3": input_data.objetosc_m3,
            "konstrukcja_kg": input_data.konstrukcja_kg,
            "sklejka_m3": input_data.sklejka_m3,
            "drewno_m3": input_data.drewno_m3,
            "plyta_m2": input_data.plyta_m2,
            "druk_m2": input_data.druk_m2,
            "led_mb": input_data.led_mb,
            "tworzywa_m2": input_data.tworzywa_m2,
            "koszty_pozostale": input_data.koszty_pozostale,
            "stopien_skomplikowania": input_data.stopien_skomplikowania,
            "rodzaj_tworzywa": input_data.rodzaj_tworzywa,
            "rodzaj_displaya": input_data.rodzaj_displaya,
        })

        user_price = form.cleaned_data.get("user_price")

        # Zapis do sesji tylko liczby dla predykcji
        self.request.session["predicted"] = float(predicted_result["predicted"])
        self.request.session["user_price"] = (
            float(user_price) if user_price not in (None, "", 0) else None
        )

        # Zapisujemy informacje o modelu w sesji
        self.request.session["model_info"] = {
            "name": predicted_result["model_name"],
            "mae": predicted_result["mae"],
            "r2": predicted_result["r2"],
            "type": predicted_result["model_type"],
        }

        submission = Submission.objects.create(
            user=self.request.user,
            input_data=input_data,
            predicted_price=float(predicted_result["predicted"]),
            user_price=float(user_price) if user_price not in (None, "", 0) else None,
        )
        self.request.session["submission_id"] = submission.pk

        return super().form_valid(form)


class EstimationResultView(LoginRequiredMixin, TemplateView):
    template_name = "estimations/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['predicted'] = self.request.session.get('predicted')
        context['user_price'] = self.request.session.get('user_price')

        # Pobranie danych modelu z sesji
        model_info = self.request.session.get('model_info', {})
        context['model_name'] = model_info.get('name')
        context['model_mae'] = model_info.get('mae')
        context['model_r2'] = model_info.get('r2')
        context['model_type'] = model_info.get('type')
        context['submission_id'] = self.request.session.get('submission_id')

        return context


class GeminiVerifyPriceView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        submission_id = request.POST.get("submission_id")
        if not submission_id:
            return JsonResponse({"error": "Missing submission id."}, status=400)

        try:
            submission = Submission.objects.select_related("input_data").get(
                pk=submission_id,
                user=request.user,
            )
        except Submission.DoesNotExist:
            return JsonResponse({"error": "Submission not found."}, status=404)

        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            return JsonResponse({"error": "GEMINI_API_KEY is not configured."}, status=500)

        prompt = _build_price_check_prompt(submission)
        client = genai.Client(api_key=api_key)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-flash-latest")
        use_google_search = getattr(settings, "GEMINI_USE_GOOGLE_SEARCH", True)
        allow_fallback_without_search = getattr(
            settings,
            "GEMINI_ALLOW_FALLBACK_WITHOUT_SEARCH",
            True,
        )
        fallback_without_search = False

        try:
            response = _request_gemini(
                client=client,
                model_name=model_name,
                prompt=prompt,
                use_google_search=use_google_search,
            )
        except Exception as exc:
            if _is_quota_error(exc) and use_google_search and allow_fallback_without_search:
                try:
                    response = _request_gemini(
                        client=client,
                        model_name=model_name,
                        prompt=prompt,
                        use_google_search=False,
                    )
                    fallback_without_search = True
                except Exception as fallback_exc:
                    if _is_quota_error(fallback_exc):
                        return JsonResponse(
                            {
                                "error": "Przekroczono limit zapytań Gemini dla tego klucza API. Spróbuj ponownie jutro lub zwiększ limit w Google AI Studio."
                            },
                            status=429,
                        )
                    return JsonResponse(
                        {"error": f"Gemini request failed: {fallback_exc}"},
                        status=502,
                    )

            elif _is_quota_error(exc):
                return JsonResponse(
                    {
                        "error": "Przekroczono limit zapytań Gemini dla tego klucza API. Spróbuj ponownie jutro lub zwiększ limit w Google AI Studio."
                    },
                    status=429,
                )
            else:
                return JsonResponse(
                    {"error": f"Gemini request failed: {exc}"},
                    status=502,
                )

        text = _extract_gemini_text(response)

        if not text:
            diagnostics = _gemini_diagnostics(response)
            return JsonResponse(
                {
                    "error": "Gemini did not return any text.",
                    "diagnostics": diagnostics,
                },
                status=502,
            )

        if fallback_without_search:
            text = (
                "Uwaga: osiągnięto limit Google Search dla Gemini, więc odpowiedź wygenerowano bez wyszukiwania online.\n\n"
                + text
            )

        return JsonResponse({"text": text})


def _build_price_check_prompt(submission):
    input_data = submission.input_data
    predicted_price = submission.predicted_price  # cena z ML

    lines = [
        "Masz podaną cenę jednostkową produkcji stojaka POS: "
        f"{predicted_price} PLN.",
        "Sprawdź, czy jest realistyczna w kontekście kosztów materiałów, robocizny i kosztów pozostałych.",
        "Nie uwzględniaj marży ani kosztów sprzedaży.",
        "Odpowiedz po polsku w trzech liniach wyświetlając również poniższe pytania:",
        "1. Czy cena predykcji jest realistyczna? (tak/nie)",
        "2. Krótki komentarz dlaczego: ",
        "3. Proponowana poprawka ceny w PLN jeśli uważasz, że jest błędna, lub napisz 'brak zmian'.",
        "",
        "Szczegóły stojaka:",
        f"- Nakład: {input_data.naklad_szt} szt.",
        f"- Objętość: {input_data.objetosc_m3} m³",
        f"- Konstrukcja: {input_data.konstrukcja_kg} kg",
        f"- Sklejka: {input_data.sklejka_m3} m³",
        f"- Drewno: {input_data.drewno_m3} m³",
        f"- Płyta: {input_data.plyta_m2} m²",
        f"- Druk: {input_data.druk_m2} m²",
        f"- LED: {input_data.led_mb} mb",
        f"- Tworzywa: {input_data.tworzywa_m2} m²",
        f"- Koszty pozostałe: {input_data.koszty_pozostale} PLN",
        f"- Stopień skomplikowania: {input_data.stopien_skomplikowania}",
        f"- Rodzaj tworzywa: {input_data.rodzaj_tworzywa}",
        f"- Rodzaj displaya: {input_data.rodzaj_displaya}",
    ]
    return "\n".join(lines)

def _extract_gemini_text(response):
    text = getattr(response, "text", None) or ""
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            continue
        collected = []
        for part in parts:
            if hasattr(part, "text") and part.text:
                collected.append(part.text)
            elif isinstance(part, dict) and part.get("text"):
                collected.append(part["text"])
        if collected:
            return "".join(collected)

    return ""


def _request_gemini(client, model_name, prompt, use_google_search):
    config_kwargs = {
        "temperature": 0.2,
        "max_output_tokens": 3072,
    }
    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )


def _is_quota_error(exc):
    message = str(exc).lower()
    return any(
        marker in message
        for marker in ("resource_exhausted", "429", "quota", "rate limit", "daily")
    )


def _gemini_diagnostics(response):
    diagnostics = {}
    prompt_feedback = getattr(response, "prompt_feedback", None)
    if prompt_feedback:
        diagnostics["prompt_feedback"] = str(prompt_feedback)

    candidates = getattr(response, "candidates", None) or []
    candidate_info = []
    for candidate in candidates:
        info = {}
        finish_reason = getattr(candidate, "finish_reason", None)
        if finish_reason:
            info["finish_reason"] = str(finish_reason)
        safety = getattr(candidate, "safety_ratings", None)
        if safety:
            info["safety_ratings"] = [str(item) for item in safety]
        if info:
            candidate_info.append(info)

    if candidate_info:
        diagnostics["candidates"] = candidate_info

    return diagnostics
