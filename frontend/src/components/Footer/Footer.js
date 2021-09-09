import {
  EuiFlexGroup,
  EuiFlexItem,
  EuiLink,
  EuiSpacer,
  EuiText
} from '@elastic/eui'
import { Link } from 'react-router-dom'

import { StyledIcon } from '..'
import {
  githubInverse,
  gridInverse,
  qsColor,
  shanghaiColor,
  theColor
} from '../../assets/images'
import { r } from '../../routes'

const Footer = props => {
  const madeWithLove = (
    <EuiText>
      <p>
        Made with <span className='footer-heart'>♥️</span> by{' '}
        <EuiLink href='https://www.linkedin.com/in/pmsoltani'>
          Pooria Soltani
        </EuiLink>
      </p>
    </EuiText>
  )
  return (
    <div className='footer-container'>
      <EuiFlexGroup justifyContent='spaceAround'>
        <EuiFlexItem grow={false}>{madeWithLove}</EuiFlexItem>
      </EuiFlexGroup>
      <EuiFlexGroup justifyContent='spaceAround'>
        <EuiFlexItem grow={false}>
          <EuiLink external href='https://www.topuniversities.com'>
            <StyledIcon type={qsColor} size='m' />
            Top Universities (QS)
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink external href='https://www.shanghairanking.com'>
            <StyledIcon type={shanghaiColor} size='m' />
            Shanghai Ranking
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink external href='https://www.timeshighereducation.com'>
            <StyledIcon type={theColor} size='m' />
            Times Higher Education (THE)
          </EuiLink>
        </EuiFlexItem>

        <EuiFlexItem grow={false}>
          <EuiLink external href='https://grid.ac'>
            <StyledIcon type={gridInverse} size='m' />
            Global Research Identifier Database (GRID)
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink external href='https://github.com/pmsoltani/rankr'>
            <StyledIcon type={githubInverse} size='m' />
            rankr on GitHub
          </EuiLink>
          <EuiSpacer size='s' />
          <Link to={r.about.url}>
            About rankr
          </Link>
        </EuiFlexItem>
      </EuiFlexGroup>
    </div>
  )
}

export default Footer
