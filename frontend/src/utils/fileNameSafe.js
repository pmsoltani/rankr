/**
 * Replaces the input string with one safe for file names.
 * @param {string} str
 * @returns {string}
 */
const fileNameSafe = str =>
  str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9-]/gi, '_')
    .toLowerCase()

export default fileNameSafe
