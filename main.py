"""Runnable UML-to-code demonstration for EcoSort AI Team 22."""
from subsystem_1_dataset_preprocessing import DatasetManager
from subsystem_2_image_recognition import ImageRecognitionService
from subsystem_3_recycling_ai import RecyclingGuidanceService
from subsystem_4_web_integration import DashboardService, IntegrationController, WasteRepository, WasteSortingWebApp

def main():
    manager=DatasetManager(); manager.initialize(); images=manager.loadDataset(); manager.validateDataset()
    processed=manager.pipeline.preprocessImages(images); split=manager.datasetSplit.splitData(processed)
    repository=WasteRepository(); dashboard=DashboardService(repository)
    controller=IntegrationController(ImageRecognitionService(),RecyclingGuidanceService(),dashboard,repository)
    app=WasteSortingWebApp(controller); app.initialize(); result=app.uploadImage(processed[0])
    print('EcoSort AI - UML to OOP demonstration')
    print('Dataset:',manager.getDatasetInfo()); print('Split:',split)
    print(app.displayResults(result)); print('Dashboard:',dashboard.getStatistics())

if __name__=='__main__': main()
