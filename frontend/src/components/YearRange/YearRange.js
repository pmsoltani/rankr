import { EuiRange } from '@elastic/eui'

const YearRange = props => {
  const { years, value, onChange } = props
  return (
    <EuiRange
      fullWidth
      min={Math.min(...years)}
      max={Math.max(...years)}
      value={value || Math.max(...years)}
      onChange={onChange}
      showTicks
    />
  )
}

export default YearRange
