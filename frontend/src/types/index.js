/**
 * @typedef {object} Acronym
 * @property {number} id
 * @property {number} institution_id
 * @property {string} acronym
 */

/**
 * @typedef {object} Alias
 * @property {number} id
 * @property {number} institution_id
 * @property {string} alias
 */

/**
 * @typedef {object} Country
 * @property {string} country
 * @property {string} country_code
 * @property {number} id
 * @property {string} region
 * @property {string} sub_region
 */

/**
 * @typedef {object} Institution
 * @property {Array.<Acronym>} acronyms
 * @property {Array.<Alias>} aliases
 * @property {string} city
 * @property {Country} country
 * @property {number} country_id
 * @property {number} established
 * @property {string} grid_id
 * @property {number} id
 * @property {Array.<Label>} labels
 * @property {string} lat
 * @property {Array.<Link>} links
 * @property {string} lng
 * @property {string} name
 * @property {Array.<Ranking>} rankings
 * @property {Array.<Ranking>} ranks
 * @property {string} soup
 * @property {string} state
 * @property {Array.<Ranking>} stats
 * @property {Array.<Type>} types
 */

/**
 * @typedef {object} Label
 * @property {number} id
 * @property {number} institution_id
 * @property {string} iso639
 * @property {string} label
 */

/**
 * @typedef {object} Link
 * @property {number} id
 * @property {number} institution_id
 * @property {string} type
 * @property {string} link
 */

/**
 * @typedef {object} Ranking
 * @property {string} field
 * @property {number} id
 * @property {number} institution_id
 * @property {string} metric
 * @property {string} ranking_system
 * @property {string} ranking_type
 * @property {string} raw_value
 * @property {string} subject
 * @property {string} value
 * @property {string} value_type
 * @property {number} year
 */

/**
 * @typedef {object} Type
 * @property {number} id
 * @property {number} institution_id
 * @property {string} type
 */
