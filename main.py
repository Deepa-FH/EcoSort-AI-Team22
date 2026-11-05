"""Print one safe error response from every EcoSort AI subsystem."""
from ecosort_testing.dataset_errors import DatasetErrorHandler, CorruptImageError
from ecosort_testing.recognition_errors import RecognitionErrorHandler, ModelNotFoundError
from ecosort_testing.recycling_ai_errors import RecyclingAIErrorHandler, MissingAPIKeyError
from ecosort_testing.web_errors import WebDashboardErrorHandler, MissingUploadError


def main() -> None:
    examples = [
        DatasetErrorHandler().handle(CorruptImageError()),
        RecognitionErrorHandler().handle(ModelNotFoundError()),
        RecyclingAIErrorHandler().handle(MissingAPIKeyError()),
        WebDashboardErrorHandler().handle(MissingUploadError()),
    ]
    print("EcoSort AI - Home Task 4 error handling")
    for result in examples:
        print(f"{result.subsystem}: {result.code} | HTTP {result.http_status} | {result.message}")


if __name__ == "__main__":
    main()
