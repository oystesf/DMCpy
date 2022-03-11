import numpy as np
from DMCpy import _tools
import h5py as hdf
from DMCpy import TasUBlibDEG


def cosd(x):
    return np.cos(np.deg2rad(x))

def sind(x):
    return np.sin(np.deg2rad(x))

def camelCase(string,split='_'):
    """Convert string to camel case from <split> seperated"""

    if not split in string:
        return string
    splitString = string.split(split)
    first = splitString[0]
    others = [x.title() for x in splitString[1:]]
    
    combi = [first]+others
    return ''.join([str(x) for x in combi])

class Sample(object):
    """Sample object to store all information of the sample from the experiment"""
    @_tools.KwargChecker()
    def __init__(self,a=1.0,b=1.0,c=1.0,alpha=90,beta=90,gamma=90,sample=None,name='Unknown',projectionVector1=None, projectionVector2 = None):
        if isinstance(sample,hdf._hl.group.Group):
            self.name = np.array(sample.get('name'))[0].decode()
            if self.name is None or self.name == '':
                self.name = 'Unknown'
            if not sample.get('orientation_matrix') is None:
                self.orientationMatrix = np.array(sample.get('orientation_matrix'))*2*np.pi
            else:
                self.orientationMatrix = np.eye(3)

            self.planeNormal = np.array(sample.get('plane_normal'))
            
            self.polarAngle = np.array(sample.get('polar_angle'))
            self.rotationAngle = np.array(sample.get('rotation_angle'))
            unitCell = sample.get('unit_cell')

            if not unitCell is None:
                self.unitCell = unitCell
            else:
                self.unitCell = [1,1,1,90,90,90]
            self.plane_vector1 = np.array(sample.get('plane_vector_1'))
            self.plane_vector2 = np.array(sample.get('plane_vector_2'))
            #crossProduct = np.cross(self.plane_vector1[:3],self.plane_vector2[:3])
            # if not np.all(np.isclose(crossProduct,[0,0,0])):
            #     self.planeNormal = crossProduct
            # self.A3Off = np.array([0.0])#
            # if not np.isclose(np.linalg.norm(self.plane_vector1[:3].astype(float)),0.0) or not np.isclose(np.linalg.norm(self.plane_vector2[:3].astype(float)),0.0): # If vectors are not zero
            #     self.projectionVector1,self.projectionVector2 = calcProjectionVectors(self.plane_vector1.astype(float),self.plane_vector2.astype(float))
            # else:
            #     self.projectionVector1,self.projectionVector2 = [np.array([1.0,0.0,0.0]),np.array([0.0,1.0,0.0])]
            # self.initialize()
            # self.calculateProjections()

            # attributes = ['azimuthal_angle','x','y','sgu','sgu_zero','sgl','sgl_zero']
            # values = [camelCase(x) for x in attributes]
            # for att, val in zip(attributes,values):
            #     setattr(self,val,np.array(sample.get(att)))
            
            
        elif np.all([a is not None,b is not None, c is not None]):
            self.unitCell = np.array([a,b,c,alpha,beta,gamma])
           
            self.polarAngle = np.array(None)
            self.rotationAngle = np.array(0)
            self.name=name
            
            r1 = projectionVector1
            r2 = projectionVector2
            self.plane_vector1 = r1
            self.plane_vector2 = r2

            self.planeNormal = np.cross(self.plane_vector1[:3],self.plane_vector2[:3])
            
            
            # cell = TasUBlib.calcCell(self.unitCell)

            # self.orientationMatrix = TasUBlib.calcTasUBFromTwoReflections(cell, r1, r2)
            # #self.orientationMatrix = TasUBlib.calcTasUBFromTwoReflections(self.cell,self.plane_vector1,self.plane_vector2)
            # self.projectionVector1,self.projectionVector2 = calcProjectionVectors(self.plane_vector1.astype(float),self.plane_vector2.astype(float))#,self.planeNormal.astype(float))
            # self.initialize()
            # self.calculateProjections()
        else:
            print(sample)
            print(a,b,c,alpha,beta,gamma)
            raise AttributeError('Sample not understood')

            
    @property
    def unitCell(self):
        return self._unitCell

    @unitCell.getter
    def unitCell(self):
        return np.array([self.a,self.b,self.c,self.alpha,self.beta,self.gamma])#self._unitCell

    @unitCell.setter
    def unitCell(self,unitCell):
        self._unitCell = unitCell
        self.a = unitCell[0]
        self.b = unitCell[1]
        self.c = unitCell[2]
        self.alpha = unitCell[3]
        self.beta  = unitCell[4]
        self.gamma = unitCell[5]
        self.updateCell()
        
    @property
    def a(self):
        return self._a

    @a.getter
    def a(self):
        return self._a

    @a.setter
    def a(self,a):
        if a>0:
            self._a = a
        else:
            raise AttributeError('Negative or null given for lattice parameter a')

    @property
    def b(self):
        return self._b

    @b.getter
    def b(self):
        return self._b

    @b.setter
    def b(self,b):
        if b>0:
            self._b = b
        else:
            raise AttributeError('Negative or null given for lattice parameter b')

    @property
    def c(self):
        return self._c

    @c.getter
    def c(self):
        return self._c

    @c.setter
    def c(self,c):
        if c>0:
            self._c = c
        else:
            raise AttributeError('Negative or null given for lattice parameter c')


    @property
    def alpha(self):
        return self._alpha

    @alpha.getter
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self,alpha):
        if alpha>0 and alpha<180:
            self._alpha = alpha
        else:
            raise AttributeError('Negative,null or above 180 degrees given for lattice parameter alpha')

    @property
    def beta(self):
        return self._beta

    @beta.getter
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self,beta):
        if beta>0 and beta<180:
            self._beta = beta
        else:
            raise AttributeError('Negative,null or above 180 degrees given for lattice parameter beta')

    @property
    def gamma(self):
        return self._gamma

    @gamma.getter
    def gamma(self):
        return self._gamma

    @gamma.setter
    def gamma(self,gamma):
        if gamma>0 and gamma<180:
            self._gamma = gamma
        else:
            raise AttributeError('Negative,null or above 180 degrees given for lattice parameter gamma')

    def updateCell(self):
        self.fullCell = TasUBlibDEG.calcCell(self.unitCell)
        self.B = TasUBlibDEG.calculateBMatrix(self.fullCell)

    def saveToHdf(self,entry):
        entry.create_dataset('name',data = [np.string_(self.name)])
        