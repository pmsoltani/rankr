import { EuiIcon } from '@elastic/eui'
import styled from 'styled-components'

const StyledIconComponent = styled(EuiIcon)`
  margin-right: 4px;
`

const StyledIcon = props => <StyledIconComponent {...props} />

export default StyledIcon
