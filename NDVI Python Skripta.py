from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterDestination
import processing


class Ndvi(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('nir', 'NIR', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poligon', 'Poligon', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('red', 'Red', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Ndvi', 'NDVI', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Raster calculator NDVI
        alg_params = {
            'FORMULA': '(a-b)/(a+b)',
            'GRIDS': parameters['nir'],
            'RESAMPLING': 3,
            'TYPE': 7,
            'USE_NODATA': False,
            'XGRIDS': parameters['red'],
            'RESULT': parameters['Ndvi']
        }
        outputs['RasterCalculatorNdvi'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ndvi'] = outputs['RasterCalculatorNdvi']['RESULT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Zonal statistics
        alg_params = {
            'COLUMN_PREFIX': 'ndvi_',
            'INPUT_RASTER': outputs['RasterCalculatorNdvi']['RESULT'],
            'INPUT_VECTOR': parameters['poligon'],
            'RASTER_BAND': 1,
            'STATS': 2
        }
        outputs['ZonalStatistics'] = processing.run('qgis:zonalstatistics', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'NDVI'

    def displayName(self):
        return 'NDVI'

    def group(self):
        return 'NDVI'

    def groupId(self):
        return 'NDVI'

    def createInstance(self):
        return Ndvi()
