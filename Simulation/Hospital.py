__author__ = 'Andrew'

import random
import simpy

def enum(**enums):
    return type('Enum', (), enums)

#*************************************************************
#*                      Business domain
#*************************************************************
ChamberType = enum(MALE=0, FEMALE=1, BOTH=2)
SexType = enum(MALE=0, FEMALE=1)

class Hospital(object):
    def __init__(self, departments):
        self.departments = departments


class Department(object):
    def __init__(self, name, chambers, service_lines):
        self.name = name
        self.chambers = chambers
        self.service_lines = service_lines


class Chamber(object):
    def __init__(self, code, capacity, type):
        self.code = code
        self.capacity = capacity
        self.type = type

drg_list = ["DRG01","DRG02","DRG03","DRG04","DRG05"]

def build_hospital():
    departments = []

    chambers = [Chamber("SURG01", 1, ChamberType.BOTH)
                ,Chamber("SURG02", 1, ChamberType.BOTH)
                ,Chamber("SURG03", 1, ChamberType.BOTH)
                ,Chamber("SURG04", 2, ChamberType.MALE)
                ,Chamber("SURG05", 2, ChamberType.FEMALE)]
    service_lines = [("SL01", 1.0), ("SL02", 1.0), ("SL03", 1.0)]
    departments.append(Department("Surgery", chambers, service_lines))

    chambers = [Chamber("INFG01", 1, ChamberType.BOTH)
                ,Chamber("INFG02", 1, ChamberType.BOTH)
                ,Chamber("INFG03", 1, ChamberType.BOTH)
                ,Chamber("INFG04", 2, ChamberType.MALE)
                ,Chamber("INFG05", 2, ChamberType.FEMALE)]
    service_lines = [("SL03", 0.9), ("SL04", 1.0), ("SL05", 1.0)]
    departments.append(Department("Infection", chambers, service_lines))

    return Hospital(departments)


def build_drg2sl():
    result = {}
    result["DRG01"] = ["SL01"]
    result["DRG02"] = ["SL02"]
    result["DRG03"] = ["SL03"]
    result["DRG04"] = ["SL04"]
    result["DRG05"] = ["SL05"]
    return result


def get_chambers_for_patient(hospital, patient):
    drg2sl = build_drg2sl()
    if patient.drg not in drg2sl:
        return []

    patient_service_line = drg2sl[patient.drg]

    depars = []
    for depar in hospital.departments:
        score = 0.0
        for sl in depar.service_lines:
            if sl[0] == patient_service_line:
                score = max(score, sl[1])
        if score > 0.0:
            depars.append((depar, score))
    depars.sort(key=lambda tup: tup[1], reverse=True)
    if len(depars) == 0:
        return []

    result = []
    for  tup in depar:
        result.append(tup[0].chambers)
    return result

#*************************************************************
#*                      Simulation code
#*************************************************************
class ResourceItem(object):
    def __init__(self, chamber, place):
        self.chamber = chamber
        self.place = place  # 0 means whole chamber
        self.patient = None

    def free(self):
        return self.patient is None


class HospitalAsResource(object):
    def __init__(self, env, hospital):
        self.env = env
        self.hospital = hospital
        self.filter_resource = self._build_resource();

    def _build_resource(self):
        """Build SimPy filter store resource to use hospital in simulation"""
        items = []
        for department in self.hospital.departments:
            for chamber in department.chambers:
                items.append(ResourceItem(chamber, 0))  # 0 means seize of whole chamber
                if chamber.capacity > 1:
                    for place in range(chamber.capacity):
                        items.append(ResourceItem(chamber, place+1))
        resource = simpy.FilterStore(self.env)
        resource.items = items
        return resource

    def request(self, patient):
        chambers = get_chambers_for_patient(self.hospital, patient)
        if len(chambers) == 0:
            print "Cannot assign a chamber to patient"

        item_for_patient = None
        for chamber in chambers:
            for item in self.filter_resource.items:
                if item.chamber != chamber:
                    continue

                if not item.free() and item.place == 0:
                    item_for_patient = None
                    break

                if not item.free() and item.place != 0 and patient.vip:
                    item_for_patient = None
                    break

                if item.free() and (
                    patient.vip and item.place == 0
                    or not patient.vip and item.chamber.capacity == 1
                    or not patient.vip and item.chamber.capacity > 1 and item.place != 0
                ):
                    item_for_patient = item

            if item_for_patient is not None:
                break

        if item_for_patient is None:
            print "Cannot assign a chamber to patient"

        #seize chamber
        print "Chamber %s seized" % item.chamber.code
        item_for_patient.patient = patient
        return self.filter_resource.get(lambda it: it == item_for_patient)

    def release(self, patient):
        pass

def source(env):
    """Generates sequence of patients"""
    number = random.randint(0, 2)
    patients = []
    for p in range(number):
        drg = drg_list[random.randint(0, len(drg_list) - 1)]
        sex = SexType.MALE if random.uniform(0, 1) > 0.51 else SexType.FEMALE
        vip = False if random.uniform(0, 1) >= 0.05 else True
        patients.append(Patient(env, drg, sex, vip))


class Patient(object):
    def __init__(self, env, drg, sex, vip = False):
        self.env = env
        self.drg = drg
        self.sex = sex
        self.vip = vip

    def enter(self):
        """Patient enters hospital"""
        pass

""" Simple hospital simulation
Hospital consists of two departments each of 5 chambers
1 time unit corresponds to an hour

Assumptions:
1) initially hospital is empty
2) hospital structure cannot be changed during simulation (e.g. add new department)
"""


print "Hospital simulation"
env = simpy.Environment()