import { EuiComboBox } from '@elastic/eui'
import React from 'react'

const CountrySelect = props => {
  const { isLoading, options = [], onSelectChange, selectedValues } = props
  const [selectedOptions, setSelectedOptions] = React.useState(selectedValues)

  React.useEffect(() => {
    selectedValues.length
      ? setSelectedOptions(selectedValues)
      : setSelectedOptions([])
  }, [selectedValues])

  const onChange = selectedOptions => {
    setSelectedOptions(selectedOptions)
    onSelectChange(selectedOptions)
  }

  const renderOption = (option, searchValue, contentClassName) => {
    const { label, value } = option
    return (
      <>
        <span
          className={`flag-icon flag-icon-${value.countryCode.toLowerCase()}`}
          style={{ fontSize: '1em', marginRight: '4px' }}
        />
        <span>{label}</span>
      </>
    )
  }

  return (
    <EuiComboBox
      compressed
      isClearable
      isLoading={isLoading}
      onChange={onChange}
      options={options}
      placeholder='Country filter'
      renderOption={renderOption}
      selectedOptions={selectedOptions}
    />
  )
}

export default CountrySelect
