import {
  EuiPanel,
  EuiFlexGroup,
  EuiFlexItem,
  EuiIcon,
  EuiLink,
  EuiText
} from '@elastic/eui'

import { InstitutionLogo } from '..'
import {
  gridDisabled,
  gridInverse,
  homeDisabled,
  homeFill,
  locationOutline,
  qsColor,
  qsDisabled,
  shanghaiColor,
  shanghaiDisabled,
  theColor,
  theDisabled,
  wikipediaDisabled,
  wikipediaInverse
} from '../../assets/images'
import { gridURL, openStreetMapURL } from '../../utils'

const PageHeader = props => {
  const { institution: inst, overview, rightSideItems } = props
  const renderLocation = (country, city, lat, lng) => {
    const url = openStreetMapURL(lat, lng)
    return (
      <EuiLink href={url} disabled={!url} target='_blank' external={false}>
        <EuiIcon type={locationOutline} size='l' />
        {city}, {country.country}
      </EuiLink>
    )
  }

  const renderLinks = links => {
    const linkTypes = {
      homepage: { icon: homeFill, iconDisabled: homeDisabled },
      grid: { icon: gridInverse, iconDisabled: gridDisabled },
      wikipedia: { icon: wikipediaInverse, iconDisabled: wikipediaDisabled },
      qs: { icon: qsColor, iconDisabled: qsDisabled },
      shanghai: { icon: shanghaiColor, iconDisabled: shanghaiDisabled },
      the: { icon: theColor, iconDisabled: theDisabled }
    }
    links = Object.assign({}, ...links.map(i => ({ [i.type]: i.link })))
    links.grid = gridURL(inst.grid_id)
    const linkElements = Object.keys(linkTypes).map(i => (
      <EuiLink
        key={i}
        href={links[i]}
        disabled={!links[i]}
        target='_blank'
        external={false}
      >
        <EuiIcon
          type={links[i] ? linkTypes[i].icon : linkTypes[i].iconDisabled}
          size='l'
        />
      </EuiLink>
    ))
    linkElements.push(
      renderLocation(inst.country, inst.city, inst.lat, inst.lng)
    )
    return linkElements
  }

  return (
    <header
      style={{ marginBottom: '24px', width: '1000px', margin: '0 auto 24px' }}
    >
      <EuiFlexGroup justifyContent='spaceBetween' wrap>
        <EuiFlexItem>
          <EuiFlexGroup>
            <EuiFlexItem grow={false} style={{ maxWidth: '112px' }}>
              <EuiPanel paddingSize='s' grow={false}>
                <InstitutionLogo
                  alt={`${inst.name} logo`}
                  institution={inst}
                  size='96px'
                />
              </EuiPanel>
            </EuiFlexItem>
            <EuiFlexItem grow={false}>
              <EuiFlexGroup>
                <EuiFlexItem grow={false}>
                  <EuiText>
                    <h1>{inst.name}</h1>
                  </EuiText>
                  <EuiText size='xs'>since {inst.established}</EuiText>
                </EuiFlexItem>
              </EuiFlexGroup>
              <EuiFlexGroup>
                <EuiFlexItem grow={false} style={{}}>
                  <EuiFlexGroup>
                    {renderLinks(inst.links).map((item, index) => (
                      <EuiFlexItem key={index} grow={false}>
                        {item}
                      </EuiFlexItem>
                    ))}
                  </EuiFlexGroup>
                </EuiFlexItem>
              </EuiFlexGroup>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiFlexItem>
        <EuiFlexItem grow={1} style={{ maxWidth: '250px' }}>
          <EuiFlexGroup wrap>
            {rightSideItems.map((item, index) => (
              <EuiFlexItem grow={false} key={index}>
                {item}
              </EuiFlexItem>
            ))}
          </EuiFlexGroup>
        </EuiFlexItem>

        <EuiFlexItem style={{ minWidth: '600px', maxWidth: '1000px' }}>
          <EuiText>{overview}</EuiText>
        </EuiFlexItem>
      </EuiFlexGroup>
    </header>
  )
}

export default PageHeader
