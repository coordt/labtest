from state import ScriptState

service_provider = {}
state_provider = {'script': ScriptState}
secret_provider = {}

__all__ = ['state_provider', 'service_provider', 'secret_provider', ]
