# -*- coding: utf-8 -*-

import re

import common.ModelConsts as Consts

_time_reg_exp = re.compile(r"^[\d]+:[\d]+[\\*]*$")
_annotation_key_reg_exp = re.compile(r"^[\\*]+$")


def validate_stop_info(stop_info_dict):
    errors = []
    if Consts.STOP_NAME not in stop_info_dict.keys():
        errors.append("Attribute \"{0}\" not exists".format(Consts.STOP_NAME))

    if Consts.STOP_ID not in stop_info_dict.keys():
        errors.append("Attribute \"{0}\" not exists".format(Consts.STOP_ID))

    if Consts.SCHEDULES_BY_DAY_TYPE not in stop_info_dict.keys():
        errors.append("Attribute \"{0}\" not exists".format(Consts.SCHEDULES_BY_DAY_TYPE))
    else:
        schedules_by_day_type = stop_info_dict[Consts.SCHEDULES_BY_DAY_TYPE]
        if len(schedules_by_day_type.keys()) == 0:
            errors.append("SchedulesByDayType has zero dayTypes")
        else:
            for day_type in schedules_by_day_type.keys():
                if day_type not in Consts.ALLOWED_DAY_TYPES:
                    errors.append("Unknown dayType: \"{0}\"".format(day_type))
                else:
                    day_type_dict = schedules_by_day_type[day_type]
                    if Consts.SCHEDULE_TIMES not in day_type_dict.keys():
                        errors.append("Attribute \"{key}\" not exists in dict of dayType=\"{day_type}\"".format(
                            key=Consts.SCHEDULE_TIMES, day_type=day_type))
                    else:
                        times = day_type_dict[Consts.SCHEDULE_TIMES]
                        for time in times:
                            if not _time_reg_exp.match(time):
                                errors.append("Time=\"{time}\" in dayType=\"{day_type}\" not match".format(
                                    time=time, day_type=day_type
                                ))
                    if Consts.SCHEDULE_ANNOTATIONS not in day_type_dict.keys():
                        errors.append("Attribute \"{key}\" not exists in dict of dayType=\"{day_type}\"".format(
                            key=Consts.SCHEDULE_ANNOTATIONS, day_type=day_type))
                    else:
                        annotations = day_type_dict[Consts.SCHEDULE_ANNOTATIONS]
                        for annotation_key in annotations.keys():
                            if not _annotation_key_reg_exp.match(annotation_key):
                                errors.append("Annotation key=\"{annotation_key}\" in dayType=\"{day_type}\" not match".format(
                                    annotation_key=annotation_key, day_type=day_type
                                ))
    return errors


def validate_transport_dict(transport_dict):
    errors = []
    if Consts.TRANSPORT_NUMBER not in transport_dict.keys():
        errors.append("Attribute \"{0}\" not exists".format(Consts.TRANSPORT_NUMBER))

    if Consts.ROUTES not in transport_dict.keys():
        errors.append("Attribute \"{0}\" not exists".format(Consts.ROUTES))
    else:
        transport_routes = transport_dict[Consts.ROUTES]

        if len(transport_routes) == 0:
            errors.append("Transport has zero routes")
        else:
            for route_dict in transport_routes:
                if Consts.ROUTE_NAME not in route_dict.keys():
                    errors.append("Attribute \"{0}\" not exists in route".format(Consts.ROUTE_NAME))
                else:
                    route_name = route_dict[Consts.ROUTE_NAME]
                    if Consts.SCHEDULES not in route_dict.keys():
                        errors.append("Attribute \"{attr}\" not exists in route \"{route_name}\"".format(
                            attr=Consts.SCHEDULES,
                            route_name=route_name
                        ))
                    else:
                        schedules = route_dict[Consts.SCHEDULES]
                        if len(schedules) == 0:
                            errors.append("Route \"{route_name}\" has zero schedules".format(route_name=route_name))
    return errors


