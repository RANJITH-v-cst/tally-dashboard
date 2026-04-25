const KEY = 'tally-dashboard:tally-url';

export function getTallyUrl(): string {
  try {
    return localStorage.getItem(KEY) ?? '';
  } catch {
    return '';
  }
}

export function setTallyUrl(url: string): void {
  try {
    if (url) localStorage.setItem(KEY, url);
    else localStorage.removeItem(KEY);
  } catch {
    // ignore (e.g. privacy mode)
  }
}
