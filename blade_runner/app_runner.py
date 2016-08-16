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
    def __init__(self):
        pass

    def apply(self, config):
        pass


class ListAction(BaseAction):
    def __init__(self, name):
        super(ListAction, self).__init__()
        self.name = name
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)

    def apply(self, config):
        for action in self.actions:
            action.apply(config)


class BundleAction(ListAction):
    def __init__(self, name):
        super(BundleAction, self).__init__(name)
        self.actions = []

    def apply(self, config):
        for action in self.actions:
            action.apply(config[action.name])


class CurlAction(BaseAction):
    def __init__(self, url, method, data_template):
        super(CurlAction, self).__init__()
        self.url = url
        self.method = method
        self.data_template = data_template

    def apply(self, config):
        logger.error("CURL -X{method} {url} -D {data_template}".format(**self.__dict__).format(**config))


class CommandAction(BaseAction):
    def __init__(self, command):
        super(CommandAction, self).__init__()
        self.command = command

    def apply(self, config):
        logger.error(self.command.format(**config))


param_factory = {
    'range': RangeParameter,
    'list': ListParameter
}

action_factory = {
    'curl': CurlAction,
    'command': CommandAction
}

def main():
    config_file = "../conf/config.yml"
    with open(config_file, "r") as f:
        config = yaml.load(f)

    for app, app_conf in config.iteritems():
        app_param = BundleParameter(app)
        app_action = BundleAction(app)
        for bundle_name, bundle_conf in app_conf.iteritems():
            bundle_param = BundleParameter(bundle_name)
            for param_name, param_value in bundle_conf['params'].iteritems():
                param_type = param_value.pop('type')
                param_cls = param_factory.get(param_type)
                if not param_cls:
                    logger.error("param type %s not exists", param_type)
                    raise Exception("param type %s not exists" % param_type)

                bundle_param.add_param(param_cls(name=param_name, **param_value))
            app_param.add_param(bundle_param)

            bundle_action = ListAction(bundle_name)
            for action_value in bundle_conf['actions']:
                action_type = action_value.pop('type')
                action_cls = action_factory.get(action_type)
                if not action_cls:
                    logger.error("action type %s not exists", action_type)
                    raise Exception("action type %s not exists" % action_type)

                bundle_action.add_action(action_cls(**action_value))
            app_action.add_action(bundle_action)

        for app_config in app_param.apply():
            app_action.apply(app_config)


if __name__ == "__main__":
    logging.basicConfig()
    main()
