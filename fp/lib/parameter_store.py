# Import custom modules
import store


convertByName = {
    # Register images
    'path': str,
    'multispectral image': str,
    'panchromatic image': str,
    'positive location': str,
    # Define regions
    'window length in meters': float,
    'region length in windows': int,
    'test fraction per region': float,
    'image name': str,
    'coverage fraction': float,
    'coverage offset': int,
    'multispectral region frames': store.unstringifyNestedIntegerList,
    'region path': str,
    # Sample regions
    'example count per region': int,
    'multispectral pixel shift value': int,
    'shift count': int,
    'region name': str,
    # Extract windows
    'window length in meters': float,
    'window label': int,
    'window center path': str,
    # Combine datasets
    'window names': store.unstringifyStringList,
    'patch names': store.unstringifyStringList,
    'training size': int,
    'test size': int,
    'positive fraction': float,
    # Train classifiers
    'classifier module name': str,
    'dataset name': str,
    'feature module name': str,
    'feature class name': str,
    'connection table0 path': store.verifyPath,
    'connection table1 path': store.verifyPath,
    'hidden count': int,
    'iteration count': int,
    'ratio range': str,
    'kernel range': str,
    'which layer combination': int,
    'boost count': int,
    # Scan images
    'classifier name': str,
    'scan ratio': float,
    # Cluster probabilities
    'iteration count per burst': int,
    'maximum diameter in meters': float,
    'minimum diameter in meters': float,
    'evaluation radius in meters': float,
    'probability name': str,
    # Analyze scans
    'patch count per region': int,
    'minimum percent correct': float,
    # Evaluate scans
    'evaluation radius in meters list': store.unstringifyFloatList,
    'evaluation length in meters list': store.unstringifyFloatList,
}


def convert(function):
    def wrapper(*args, **kwargs):
        parameterName = function(*args, **kwargs)
        convert = convertByName[parameterName]
        self = args[0]
        return convert(self.parameterByName[parameterName])
    return wrapper
