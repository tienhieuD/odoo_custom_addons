/** One identifier per browser tab / page load: lets a tab ignore the notification of its own save. */
export const DWO_TAB_ID = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
export const RECORD_PRESENCE_CHANNEL_KEY = "dwo_record_presence";
