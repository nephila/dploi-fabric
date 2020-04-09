from configparser import NoOptionError, NoSectionError, RawConfigParser

_UNSET = object()


class EnvConfigParser(RawConfigParser):
    """ A config parser that can handle "namespaced" sections. Example:

    [base]
    name = base

    [base:some-env]
    name = some-env

    """

    def _concat(self, parent, child):
        return "%s:%s" % (parent, child)

    def items(self, section=_UNSET, raw=False, vars=None, env=None):
        items = {}
        try:
            items.update(dict(super().items(section, raw, vars)))
        except NoSectionError:
            pass
        if env:
            try:
                env_items = dict(super().items(self._concat(section, env), raw, vars))
                items.update(env_items)
            except NoSectionError:
                pass
        if not items:
            raise NoSectionError(self._concat(section, env) if env else section)
        return tuple(items.items())

    def get(self, section, option, *, raw=False, vars=None, fallback=_UNSET, env=None):
        if env and self.has_section(self._concat(section, env)):
            try:
                return super().get(self._concat(section, env), option, raw=raw, vars=vars, fallback=fallback)
            except NoOptionError:
                if not self.has_section(section):
                    raise
        return super().get(section, option, raw=raw, vars=vars, fallback=fallback)

    def _get(self, section, conv, option, env=None):
        return conv(self.get(section, option, env=env))

    def getint(self, section, option, *, raw=False, vars=None, fallback=_UNSET, env=None, **kwarg):
        return self._get(section, int, option, env)

    def getfloat(self, section, option, *, raw=False, vars=None, fallback=_UNSET, env=None, **kwargs):
        return self._get(section, float, option, env)

    def getboolean(self, section, option, *, raw=False, vars=None, fallback=_UNSET, env=None, **kwargs):
        v = self.get(section, option, env=env)
        return self._convert_to_boolean(v)

    def has_section(self, section, env=None, strict=False):
        if not env:
            return super().has_section(section)
        return (not strict and super().has_section(section)) or super().has_section(self._concat(section, env))

    def section_namespaces(self, section):
        namespaces = []
        for s in self.sections():
            s = s.split(":")
            if s[0] == section:
                if len(s) == 1:
                    namespaces.append("main")
                else:
                    namespaces.append(s[1])
        return namespaces

    def _interpolate(self, section, option, rawval, vars):
        return rawval
