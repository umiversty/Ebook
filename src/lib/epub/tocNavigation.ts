export type MenuAction =
  | { type: 'move'; index: number }
  | { type: 'select' }
  | { type: 'close' }
  | { type: 'noop' };

export function interpretMenuKey(key: string, currentIndex: number, total: number): MenuAction {
  if (total <= 0) return { type: 'noop' };
  switch (key) {
    case 'ArrowDown':
      return { type: 'move', index: (currentIndex + 1) % total };
    case 'ArrowUp':
      return { type: 'move', index: currentIndex - 1 < 0 ? total - 1 : currentIndex - 1 };
    case 'Home':
      return { type: 'move', index: 0 };
    case 'End':
      return { type: 'move', index: total - 1 };
    case 'Enter':
    case ' ': {
      return { type: 'select' };
    }
    case 'Escape':
      return { type: 'close' };
    default:
      return { type: 'noop' };
  }
}
