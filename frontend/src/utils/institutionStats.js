import '../types'
import renderValue from './renderValue'

const labels = {
  '# FTE Students': 'Total Students',
  '# Students per Staff': 'Students per Staff',
  '% International Students': 'Intl. Students',
  '% Female Students': 'Female Students'
}

/**
 * Modifies the institution's stats array to be rendered by components.
 * @param {Array.<Ranking>} stats
 * @returns {Array.<{key: string, title: string, description: string}>}
 */
const institutionStats = stats =>
  stats.map(item => ({
    key: item.id.toString(),
    title: renderValue(item.value, item.value_type),
    description: labels[item.metric]
  }))

export default institutionStats
