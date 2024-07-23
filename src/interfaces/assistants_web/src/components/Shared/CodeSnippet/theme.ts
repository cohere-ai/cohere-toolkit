type style = { [key: string]: React.CSSProperties };

export default {
  hljs: {
    display: 'block',
    overflowX: 'auto',
    padding: '0.5em',
    color: '#424242',
    background: 'transparent',
  },
  'hljs-comment': {
    color: '#616161',
    fontStyle: 'italic',
  },
  'hljs-quote': {
    color: '#CA492D',
    fontStyle: 'italic',
  },
  'hljs-keyword': {
    color: '#2D4CB9',
  },
  'hljs-selector-tag': {
    color: '#AFA694',
  },
  'hljs-literal': {
    color: '#9B60AA',
  },
  'hljs-subst': {
    color: '#9B60AA',
  },
  'hljs-number': {
    color: '#39594D',
  },
  'hljs-string': {
    color: '#CA492D',
  },
  'hljs-doctag': {
    color: '#CA492D',
  },
  'hljs-selector-id': {
    color: '#39594D',
  },
  'hljs-selector-class': {
    color: '#39594D',
  },
  'hljs-section': {
    color: '#39594D',
  },
  'hljs-type': {
    color: '#39594D',
  },
  'hljs-params': {
    color: '#9B60AA',
  },
  'hljs-title': {
    color: '#9B60AA',
    fontWeight: 'bold',
  },
  'hljs-tag': {
    color: '#9B60AA',
    fontWeight: 'normal',
  },
  'hljs-name': {
    color: '#9B60AA',
    fontWeight: 'normal',
  },
  'hljs-attribute': {
    color: '#FF7759',
    fontWeight: 'normal',
  },
  'hljs-variable': {
    color: '#FF7759',
  },
  'hljs-template-variable': {
    color: '#FF7759',
  },
  'hljs-regexp': {
    color: '#9B60AA',
  },
  'hljs-link': {
    color: '#9B60AA',
  },
  'hljs-symbol': {
    color: '#990073',
  },
  'hljs-bullet': {
    color: '#990073',
  },
  'hljs-built_in': {
    color: '#2D4CB9',
  },
  'hljs-builtin-name': {
    color: '#2D4CB9',
  },
  'hljs-meta': {
    color: '#39352E',
    fontWeight: 'bold',
  },
  'hljs-deletion': {
    background: '#B20000',
  },
  'hljs-addition': {
    background: '#05690D',
  },
  'hljs-emphasis': {
    fontStyle: 'italic',
  },
  'hljs-strong': {
    fontWeight: 'bold',
  },
  linenumber: {
    color: '#616161',
  },
} as style;
