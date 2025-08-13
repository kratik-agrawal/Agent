import React, { useState } from 'react'
import axios from 'axios';

type ComponentProps = {
    url: string,
    url2: string
}


export default function useGetShort(props: ComponentProps) {

    const { url, url2 } = props

    const fetchShortUrl = async (longUrl: string) => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/shorten', {
                longUrl,
              });
              const url = response.data.shortened_url
              console.log("response", url)
            return url
        } catch (error) {
            console.error('Failed to shorten URL:', error);
        }
    }

    return { fetchShortUrl };
}