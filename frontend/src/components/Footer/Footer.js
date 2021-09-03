import {
  EuiFlexGroup,
  EuiFlexItem,
  EuiHorizontalRule,
  EuiLink,
  EuiPanel,
  EuiText
} from '@elastic/eui'

const Footer = props => {
  const madeWithLove = (
    <EuiText>
      <p>
        Made with <span class='footer-heart'>♥️</span> by{' '}
        <EuiLink href='https://www.linkedin.com/in/pmsoltani'>
          Pooria Soltani
        </EuiLink>
      </p>
    </EuiText>
  )
  return (
    <div className='footer-container'>
      <EuiHorizontalRule size='full' />
      <EuiFlexGroup justifyContent='spaceAround'>
        <EuiFlexItem grow={false}>{madeWithLove}</EuiFlexItem>
      </EuiFlexGroup>
    </div>
  )
}

export default Footer
