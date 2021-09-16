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
  appLogoInverse,
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
        <EuiLink href='https://www.linkedin.com/in/pmsoltani' target='_blank'>
          Pooria Soltani
        </EuiLink>
      </p>
    </EuiText>
  )
  return (
    <footer className='footer-container'>
      <EuiFlexGroup
        justifyContent='spaceBetween'
        gutterSize='l'
        style={{ maxWidth: '1200px', margin: 'auto' }}
      >
        <EuiFlexItem grow={false}>
          <img src={appLogoInverse} alt='rankr logo' style={{ height: 36 }} />
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiLink
            external
            href='https://www.topuniversities.com'
            target='_blank'
          >
            <StyledIcon type={qsColor} size='m' />
            Top Universities (QS)
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink
            external
            href='https://www.shanghairanking.com'
            target='_blank'
          >
            <StyledIcon type={shanghaiColor} size='m' />
            Shanghai Ranking
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink
            external
            href='https://www.timeshighereducation.com'
            target='_blank'
          >
            <StyledIcon type={theColor} size='m' />
            Times Higher Education (THE)
          </EuiLink>
        </EuiFlexItem>

        <EuiFlexItem grow={false}>
          <EuiLink external href='https://grid.ac' target='_blank'>
            <StyledIcon type={gridInverse} size='m' />
            Global Research Identifier Database (GRID)
          </EuiLink>
          <EuiSpacer size='s' />
          <EuiLink
            external
            href='https://github.com/pmsoltani/rankr'
            target='_blank'
          >
            <StyledIcon type={githubInverse} size='m' />
            rankr on GitHub
          </EuiLink>
          <EuiSpacer size='s' />
          <Link to={r.about.url}>About rankr</Link>
        </EuiFlexItem>
      </EuiFlexGroup>
      <EuiFlexGroup justifyContent='spaceAround'>
        <EuiFlexItem grow={false}>{madeWithLove}</EuiFlexItem>
      </EuiFlexGroup>
    </footer>
  )
}

export default Footer
