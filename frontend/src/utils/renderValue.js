/**
 * Formats the numerical value based on valueType.
 * @param {string} value
 * @param {string} valueType
 * @returns {string}
 */
const renderValue = (value, valueType) => {
  if (valueType === 'percent') return `${value}%`
  if (valueType === 'integer') return parseInt(value).toLocaleString()
  if (valueType === 'decimal') return parseFloat(value).toLocaleString()
}

export default renderValue
