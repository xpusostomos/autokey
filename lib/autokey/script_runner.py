import threading
from pathlib import Path

import datetime
import traceback
import typing
import time
# from lib.autokey.model.store import Store
# from lib.autokey.service import threaded
from lib.autokey.model.store import Store

logger = __import__("autokey.logger").logger.get_logger(__name__)

def threaded(f):

    def wrapper(*args, **kwargs):
        t = threading.Thread(target=f, args=args, kwargs=kwargs, name="Phrase-thread")
        t.setDaemon(False)
        t.start()

    wrapper.__name__ = f.__name__
    wrapper.__dict__ = f.__dict__
    wrapper.__doc__ = f.__doc__
    wrapper._original = f  # Store the original function for unit testing purposes.
    return wrapper

class SimpleScript:
    def __init__(self, path, code):
        self.path = path
        self.code = code
        self.store = Store()


class ScriptErrorRecord:
    """
    This class holds a record of an error that caused a user Script to abort and additional meta-data .
    """
    def __init__(self, script: typing.Union[SimpleScript, Path], error_traceback: str,
                 start_time: datetime.time, error_time: datetime.time):
        self.script_name = script.path if isinstance(script, SimpleScript) else str(script)
        self.error_traceback = error_traceback
        self.start_time = start_time
        self.error_time = error_time


class ScriptRunner:

    def __init__(self, scope, app):
        self.scope = scope
        # self.mediator = mediator
        self.app = app
        self.error_records = []  # type: typing.List[ScriptErrorRecord]
        # self.scope = globals()
        # self.scope["highlevel"] = scripting.highlevel
        # self.scope["keyboard"] = scripting.keyboard.Keyboard(mediator)
        # self.scope["mouse"] = scripting.mouse.Mouse(mediator)
        # self.scope["system"] = scripting.system.System()
        # self.scope["window"] = scripting.window.Window(mediator)
        # self.scope["engine"] = scripting.engine.Engine(app.configManager, self)
        # self.scope["dialog"] = scripting.Dialog()
        # self.scope["clipboard"] = scripting.Clipboard(app)

        self.engine = self.scope["engine"]

    def clear_error_records(self):
        self.error_records.clear()

    @threaded
    def execute_script(self, script: SimpleScript):
        logger.debug("Script runner executing: %r", script)

        scope = self.scope.copy()
        scope["store"] = script.store

        # backspaces, trigger_character = script.process_buffer(buffer)
        # self.mediator.send_backspace(backspaces)
        # self._set_triggered_abbreviation(scope, buffer, trigger_character)
        if script.path is not None:
            # Overwrite __file__ to contain the path to the user script instead of the path to this service.py file.
            scope["__file__"] = script.path
        self._execute(scope, script)

        # self.mediator.send_string(trigger_character)

    # @threaded
    # def execute_match(self, script: SimpleScript, scope, buffer=''):
    #     logger.debug("Script runner executing match: %r", script)
    #
    #     scope["store"] = script.store
    #     if script.match_path is not None:
    #         Overwrite __file__ to contain the path to the user script instead of the path to this service.py file.
            # scope["__file__"] = script.match_path
        # self._execute_match(scope, script)
        # It would be nice to return the result here, but @threaded eats the return
        # print("match result: " + str(scope["window"].match))

    @threaded
    def execute_path(self, path: Path):
        logger.debug("Script runner executing: {}".format(path))
        scope = self.scope.copy()
        # Overwrite __file__ to contain the path to the user script instead of the path to this service.py file.
        scope["__file__"] = str(path.resolve())
        self._execute(scope, path)

    def _record_error(self, script: typing.Union[SimpleScript, Path], start_time: time.time):
        error_time = datetime.datetime.now().time()
        logger.exception("Script error")
        traceback_str = traceback.format_exc()
        error_record = ScriptErrorRecord(script=script, error_traceback=traceback_str, start_time=start_time, error_time=error_time)
        self.error_records.append(error_record)
        self.app.notify_error(error_record)

    def _execute(self, scope, script: typing.Union[SimpleScript, Path]):
        start_time = datetime.datetime.now().time()
        # noinspection PyBroadException
        try:
            compiled_code = self._compile_script(script)
            exec(compiled_code, scope)
        except Exception:  # Catch everything raised by the User code. Those Exceptions must not crash the thread.
            self._record_error(script, start_time)

    # def _execute_match(self, scope, script: typing.Union[SimpleScript, Path]):
    #     start_time = datetime.datetime.now().time()
    #     noinspection PyBroadException
        # try:
        #     compiled_code = self._compile_match(script)
        #     exec(compiled_code, scope)
        # except Exception:  # Catch everything raised by the User code. Those Exceptions must not crash the thread.
        #     self._record_error(script, start_time)

    @staticmethod
    def _compile_script(script: typing.Union[SimpleScript, Path]):
        script_code, script_name = ScriptRunner._get_script_source_code_and_name(script)
        compiled_code = compile(script_code, script_name, 'exec')
        return compiled_code

    # @staticmethod
    # def _compile_match(script: typing.Union[SimpleScript, Path]):
    #     script_code, script_name = ScriptRunner._get_match_source_code_and_name(script)
    #     compiled_code = compile(script_code, script_name, 'exec')
    #     return compiled_code

    @staticmethod
    def _get_script_source_code_and_name(script: typing.Union[SimpleScript, Path]) -> typing.Tuple[str, str]:
        if isinstance(script, Path):
            script_code = script.read_text()
            script_name = str(script)
        elif isinstance(script, SimpleScript):
            script_code = script.code
            if script.path is None:
                script_name = "<string>"
            else:
                script_name = str(script.path)
        else:
            raise TypeError(
                "Unknown script type passed in, expected one of [autokey.model.Script, pathlib.Path], got {}".format(
                    type(script)))
        return script_code, script_name

    # @staticmethod
    # def _get_match_source_code_and_name(script: typing.Union[SimpleScript, Path]) -> typing.Tuple[str, str]:
    #     if isinstance(script, Path):
    #         script_code = script.read_text()
    #         script_name = str(script)
    #     else:
    #         script_code = script.match_code
    #         if script.path is None:
    #             script_name = "<string>"
    #         else:
    #             script_name = str(script.match_path)
    #     return script_code, script_name

    # @staticmethod
    # def _set_triggered_abbreviation(scope: dict, buffer: str, trigger_character: str):
    #     """Provide the triggered abbreviation to the executed script, if any"""
    #     engine = scope["engine"]  # type: autokey.scripting.Engine
    #     if buffer:
    #         triggered_abbreviation = buffer[:-len(trigger_character)]
    #
    #         logger.debug(
    #             "Triggered a Script by an abbreviation. Setting it for engine.get_triggered_abbreviation(). "
    #             "abbreviation='{}', trigger='{}'".format(triggered_abbreviation, trigger_character)
    #         )
    #         engine._set_triggered_abbreviation(triggered_abbreviation, trigger_character)

    def run_subscript(self, script: typing.Union[SimpleScript, Path]):
        scope = self.scope.copy()
        if isinstance(script, SimpleScript):
            scope["store"] = script.store
            scope["__file__"] = str(script.path)
        else:
            scope["__file__"] = str(script.resolve())

        compiled_code = self._compile_script(script)
        exec(compiled_code, scope)
