import React from 'react'
import { NavigationType } from './types'
import Link from 'next/link'

const navigation: NavigationType[] = [
  { name: "Home", href: "/", id: 1 },
  { name: "Face Library", href: "/facelibrary", id: 2 },
  { name: "About", href: "/about", id: 3 },

]

const header = () => {
  return (
    <header>
      {/* style={{ ["background-color" as any]: "#aacf77" }} */}
      <div className='container-fluid bg-gray-200'>
      <div className='container'>
        <div className='row d-flex align-items-center justify-content-center'>
          <div className='col-auto text-center'>
            <h2 className='text-blue-500 mb-0'>cAIm</h2>
            <p className='text-xs mt-0'>Camera with AI in the Middle</p>
          </div>
          <div className='col-auto'>
            {/* logo */}
            <Link href="/">
              <img className="logo" src='https://www.secureauth.com/wp-content/uploads/2024/07/sa-resource-customer-story-bass-pro-shops.jpg' alt="logo" />
            </Link>
          </div>
          <div className='col-auto text-center'>
            <nav>
              <div className='flex gap-x-12'>
                {navigation.map((item: NavigationType) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className='text-sm font-semibold leading-6'>
                    {item.name}
                  </a>
                ))

                }
              </div>
            </nav>
          </div>
        </div>
      </div>
      </div>
    </header>
  )
}

export default header