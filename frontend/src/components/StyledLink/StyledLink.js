import { Link } from 'react-router-dom'
import { EuiLink } from '@elastic/eui'
import styled from 'styled-components'

const StyledLinkComponent = styled(Link)`
  text-decoration: inherit;

  &:focus,
  &:hover,
  &:visited,
  &:link,
  &:active {
    text-decoration: none !important;
    font-family: 'Sahel'
  }
`

const StyledLink = props => (
  <EuiLink>
    <StyledLinkComponent {...props} />
  </EuiLink>
)
export default StyledLink
