import { useSyncExternalStore } from "react";

const SET_GLOBALS_EVENT_TYPE = "openai:set_globals";

export function useOpenAiGlobal(key) {
  return useSyncExternalStore(
    (onChange) => {
      const handler = (event) => {
        const value = event.detail.globals?.[key];
        if (value !== undefined) onChange();
      };
      window.addEventListener(SET_GLOBALS_EVENT_TYPE, handler, {
        passive: true,
      });
      return () =>
        window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handler);
    },
    () => window.openai?.[key],
    () => window.openai?.[key]
  );
}
