import { EuiIcon, EuiSuperSelect } from '@elastic/eui'
import React from 'react'
import { qsColor, shanghaiColor, theColor } from '../../assets/images'

import * as c from '../../config'

const rankingSystemIcons = {
  qs: qsColor,
  shanghai: shanghaiColor,
  the: theColor
}

const SuperSelect = props => {
  const {
    isLoading,
    options: rawOptions = [],
    onSelectChange,
    selectedValue
  } = props
  const [options, setOptions] = React.useState([])
  const [selectedOption, setSelectedOption] = React.useState(selectedValue)

  React.useEffect(() => {
    if (rawOptions.length) {
      setOptions(
        rawOptions.map(i => ({
          value: i,
          inputDisplay: Object.keys(c.rankingSystems).includes(i) ? (
            <>
              <EuiIcon
                type={rankingSystemIcons[i]}
                style={{ marginRight: 4 }}
              />
              {c.rankingSystems[i].alias}
            </>
          ) : (
            i
          )
        }))
      )
    }
  }, [rawOptions])

  React.useEffect(() => {
    if (selectedValue) setSelectedOption(selectedValue)
  }, [selectedValue])

  const onChange = value => {
    setSelectedOption(value)
    onSelectChange(value)
  }

  return (
    <EuiSuperSelect
      compressed
      fullWidth
      isLoading={isLoading}
      onChange={value => onChange(value)}
      options={options}
      valueOfSelected={selectedOption}
    />
  )
}

export default SuperSelect
