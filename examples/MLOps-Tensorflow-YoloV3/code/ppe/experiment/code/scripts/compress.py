import os
from zipfile import ZipFile


def zipFolder(zipname, folder):
    with ZipFile(zipname, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath)

def unzipFolder(zip_path):
    zip_file = zip_path
    zip = ZipFile(zip_path, 'r')
    zip.extractall()
    zip.close()

if __name__ == '__main__':
    zipFolder("grtruth.zip","mAP/ground-truth")
    unzipFolder('grtruth.zip')