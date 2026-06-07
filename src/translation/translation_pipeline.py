from src.cache import TranslationCache
from src.ocr import OCRService
from src.services.history_service import HistoryService
from src.translation.translation_service import TranslationService


class TranslationPipeline:

    def __init__(self) -> None:
        self.ocr = OCRService()
        self.translator = TranslationService()
        self.cache = TranslationCache()
        self.history = HistoryService()

    def process_image(self, image) -> str:
        source_text = self.ocr.extract_text(image)

        if not source_text:
            return ""

        cached = self.cache.get(source_text)
        if cached:
            return cached

        translated = self.translator.translate(source_text)

        self.cache.set(source_text, translated)
        self.history.add(source_text, translated)

        return translated
