import os
from imgserver import imgengine, persistence
from imgserver.imgengine import security
from imgserver.imgengine.transformationrequest import TransformationRequest
from imgserver.imgengine.imagerequestprocessor import ImageRequestProcessor
from imgserver.imgengine.imagerequestprocessor import IImageRequestProcessor
from imgserver.persistence.persistenceprovider import PersistenceProvider,IPersistenceProvider
from imgserver.persistence.itemrepository import ItemRepository, IItemRepository

class ServiceConfiguration(object):
    def __init__(self, data_directory, dburi, allowed_sizes, drop_data=False):
        self.data_directory = data_directory
        self.dburi = dburi
        self.allowed_sizes = allowed_sizes
        self.drop_data = drop_data

class ImageServerFactory(object):
    def __init__(self, config):
        super(ImageServerFactory, self)
        self.__persistenceProvider = None
        self.__itemRepository = None
        self.__imageProcessor = None
        self.__config = config

    def getPersistenceProvider(self):
        return self.__persistenceProvider


    def getItemRepository(self):
        return self.__itemRepository


    def getImageProcessor(self):
        return self.__imageProcessor

    def createImageServer(self):
        self.__persistenceProvider = IPersistenceProvider(PersistenceProvider(self.__config.dburi))
        
        self.__itemRepository = IItemRepository(ItemRepository(self.__persistenceProvider))
        self.__imageProcessor = IImageRequestProcessor(ImageRequestProcessor(self.__itemRepository, self.__persistenceProvider, self.__config.data_directory, self.__config.drop_data))
        self.__imageProcessor.prepareTransformation =  security.imageTransformationSecurityDecorator(self.__config.allowed_sizes)(self.__imageProcessor.prepareTransformation)
        
        return self.__imageProcessor
    
    persistenceProvider = property(getPersistenceProvider, None, None, "PersistenceProvider's Docstring")
    itemRepository = property(getItemRepository, None, None, "ItemRepository's Docstring")
    imageProcessor = property(getImageProcessor, None, None, "ImageProcessor's Docstring")
