import pefile
import numpy as np

def extract_features(file_path):

    try:
        pe = pefile.PE(file_path)

        features = []

        # Basic PE features
        features.append(pe.FILE_HEADER.NumberOfSections)
        features.append(pe.FILE_HEADER.TimeDateStamp)
        features.append(pe.OPTIONAL_HEADER.SizeOfCode)
        features.append(pe.OPTIONAL_HEADER.SizeOfImage)
        features.append(pe.OPTIONAL_HEADER.AddressOfEntryPoint)

        # Pad to 519 features
        while len(features) < 519:
            features.append(0)

        return np.array(features).reshape(1, -1)

    except Exception as e:
        print("Error reading PE file:", e)
        return None