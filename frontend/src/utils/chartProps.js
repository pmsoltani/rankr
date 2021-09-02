import { rankingSystems, scoreAliases } from '../config'
import '../types'

/**
 * Adds missing keys to objects nested inside a parent object.
 * @param {object} obj
 * @param {} [missingValue=null] the value for the missing keys
 * @returns {object}
 */
const addMissingKeys = (obj, missingValue = null) => {
  let allKeys = new Set()
  Object.values(obj).forEach(item => {
    allKeys = new Set([...allKeys, ...Object.keys(item)])
  })
  const allKeysObject = Object.fromEntries(
    [...allKeys].map(key => [key, missingValue])
  )
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [
      k,
      Object.assign({}, allKeysObject, v)
    ])
  )
}

/**
 * Reforms raw API data to be displayed by ApexCharts
 * @param {Array.<Ranking>} rawData
 * @param {string} key
 * @param {string} seriesKey
 * @param {string} valueKey
 * @returns {{
 *   categories: Array.<string|number>, series: Array, colors: Array.<string>
 * }}
 */
export const rankChartProps = (
  rawData,
  key = 'year',
  seriesKey = 'ranking_system',
  valueKey = 'value'
) => {
  let data = Object.fromEntries(rawData.map(i => [i[key], {}]))
  rawData.forEach(i => {
    data[i[key]][i[seriesKey]] = i[valueKey]
  })
  data = addMissingKeys(data)

  const categories = Object.keys(data).sort((a, b) => a - b)
  const seriesNames = [...new Set(rawData.map(i => i[seriesKey]))].sort(
    (a, b) => {
      const sortingArr = Object.keys(rankingSystems)
      return sortingArr.indexOf(a) - sortingArr.indexOf(b)
    }
  )
  const series = seriesNames.map(seriesName => ({
    name: rankingSystems[seriesName].alias,
    data: Object.values(data).map(i => i[seriesName])
  }))
  const colors = seriesNames.map(i => rankingSystems[i].color)
  return { categories, series, colors }
}

/**
 * Reforms raw API data to be displayed by ApexCharts
 * @param {Array.<Ranking>} rawData
 * @param {Object.<string, any>} filters
 * @param {string} key
 * @param {string} valueKey
 * @returns @returns {{
 *   categories: Array.<string|number>, series: Array, colors: Array.<string>
 * }}
 */
export const scoreChartProps = (
  rawData,
  filters,
  key = 'metric',
  valueKey = 'value'
) => {
  const filteredData = rawData
    .filter(i => Object.entries(filters).every(([k, v]) => i[k] === v))
    .sort((a, b) => {
      const sortingArr = Object.keys(scoreAliases[a.ranking_system])
      return (
        a.ranking_system.localeCompare(b.ranking_system) ||
        sortingArr.indexOf(a.metric) - sortingArr.indexOf(b.metric)
      )
    })
  const data = Object.fromEntries(
    filteredData.map(i => {
      const rankingSystem = rankingSystems[i.ranking_system].alias
      const score = scoreAliases[i.ranking_system][i[key]]
      return [`${rankingSystem}: ${score}`, i]
    })
  )
  const categories = Object.keys(data)
  const series = [
    { name: 'Scores', data: Object.values(data).map(i => i[valueKey]) }
  ]
  const colors = categories.map(
    i => rankingSystems[i.split(':')[0].toLowerCase()].color
  )
  return { categories, series, colors }
}