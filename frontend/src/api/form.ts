export const joinList = (values?: string[] | null) => (values || []).join(', ');

export const parseList = (value?: string | string[] | null) => {
  if (Array.isArray(value)) return value;
  return (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
};

export const toJsonText = (value: unknown) => JSON.stringify(value ?? {}, null, 2);

export const parseJson = <T>(value: string, fallback: T): T => {
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
};
