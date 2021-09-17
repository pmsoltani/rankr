import { saveAs } from 'file-saver'
import React from 'react'
import Chart from 'react-apexcharts'
import watermark from 'watermarkjs'

import { appLogoSmall, download } from '../../assets/images'
import { scoreAliases } from '../../config'

const BarChart = props => {
  const { chartTitle = 'Score chart', categories, series, colors } = props
  const options = {
    chart: {
      id: 'score-chart',
      toolbar: {
        tools: {
          download: false,
          customIcons: [
            {
              icon: `<img src="${download}" width="20">`,
              index: 0,
              title: 'Download PNG',
              class: 'custom-icon',
              click: (chart, options, e) => {
                chart.dataURI().then(({ imgURI }) => {
                  watermark([imgURI, appLogoSmall])
                    .image(watermark.image.lowerLeft(0.5))
                    .then(img => saveAs(img.src, 'image.png'))
                })
              }
            }
          ]
        }
      }
    },
    colors: colors,
    dataLabels: {
      enabled: true,
      formatter: v => (v ? Math.round(v) : undefined),
      style: { colors: ['#343741'] }
    },
    legend: { show: false },
    plotOptions: {
      bar: {
        borderRadius: 4,
        dataLabels: { position: 'top' },
        distributed: true
      }
    },
    title: { text: chartTitle },
    tooltip: {
      x: {
        formatter: (value, { dataPointIndex, w }) => {
          const rankingSystem = value.split(':')[0].trim()
          const metric = value.split(':')[1].trim()
          const fullMetric = Object.keys(
            scoreAliases[rankingSystem.toLowerCase()]
          ).find(
            key => scoreAliases[rankingSystem.toLowerCase()][key] === metric
          )
          return `${rankingSystem}: ${fullMetric}`
        }
      },
      y: {
        formatter: value => value,
        title: { formatter: seriesName => undefined }
      }
    },
    xaxis: { categories: categories },
    yaxis: { decimalsInFloat: 0, max: 100, tickAmount: 5 }
  }

  return (
    <Chart
      options={options}
      series={series}
      type='bar'
      width='100%'
      height='400'
    />
  )
}

export default BarChart
