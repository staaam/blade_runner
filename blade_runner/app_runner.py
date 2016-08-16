import yaml
import logging
import itertools

logger = logging.getLogger(__name__)

__author__ = 'hubermant'

class AppRunner(object):
    pass


class Configuration(object):
    pass


class Parameter(object):
    def __init__(self, name):
        self.name = name

    def apply(self):
        pass


class RangeParameter(Parameter):
    def __init__(self, name, start, end, interval=1):
        super(RangeParameter, self).__init__(name)
        self.start = start
        self.end = end
        self.interval = interval

    def apply(self):
        return xrange(self.start, self.end, self.interval)


class ListParameter(Parameter):
    def __init__(self, name, values):
        super(ListParameter, self).__init__(name)
        self.values = values

    def apply(self):
        return self.values


class BundleParameter(Parameter):
    def __init__(self, name):
        super(BundleParameter, self).__init__(name)
        self.params = []

    def add_param(self, param):
        self.params.append(param)

    def apply(self):
        all_names = [p.name for p in self.params]
        all_params = [p.apply() for p in self.params]
        for perm in itertools.product(*all_params):
            yield dict(zip(all_names, perm))


class BaseAction(object):
    pass


param_factory = {
    'range': RangeParameter,
    'list': ListParameter
}


def main():
    config_file = "../conf/config.yml"
    with open(config_file, "r") as f:
        config = yaml.load(f)

    for app, app_conf in config.iteritems():
        app_param = BundleParameter(app)
        for bundle, bundle_conf in app_conf.iteritems():
            bundle_param = BundleParameter(bundle)
            for param_name, param_value in bundle_conf['params'].iteritems():
                param_type = param_value.pop('type')
                param_cls = param_factory.get(param_type)
                if not param_cls:
                    logger.error("param type %s not exists", param_type)
                    raise Exception("param type %s not exists" % param_type)

                bundle_param.add_param(param_cls(name=param_name, **param_value))

            app_param.add_param(bundle_param)
        test = list(app_param.apply())
        print test


    pass

if __name__ == "__main__":
    logging.basicConfig()
    main()
