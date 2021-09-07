import React from 'react'

import { uniLogo } from '../../assets/images'
import { r } from '../../routes'
import { formatURL } from '../../utils'

const InstitutionLogo = props => {
  const {
    alt = 'Institution logo',
    institution,
    size = '48px',
    ...rest
  } = props
  const logoURL = `${r.institutionLogo.url}/${institution.grid_id}`
  const [imgSrc, setImgSrc] = React.useState(formatURL(logoURL, {}))
  const onError = () => setImgSrc(uniLogo)

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        height: size,
        width: size
      }}
    >
      <img
        alt={alt}
        src={imgSrc}
        onError={onError}
        style={{ maxHeight: size, maxWidth: size, margin: 'auto' }}
        {...rest}
      />
    </div>
  )
}

export default InstitutionLogo
