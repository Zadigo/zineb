import { Ref } from 'vue'

declare interface listenerOptions {
    onopen?: (e: Event) => void
    onclose?: (e: Event) => void
    onmessage?: (e: Event) => void
    onerror?: (e: Event) => void
}

/** Load component from "views" folder */ 
declare function loadView (name: string): Promise<any>
/** Load component from "layouts" folder */ 
declare function loadLayout (name: string): Promise<any>
/** Load component from "components" folder */ 
declare function loadComponent (name: string): Promise<any>
/** Scroll to the top of a page */
declare function scrollToTop (): void
/** Timeout for async functions */
declare function asyncTimeout (ms: number): Promise<any>

/** Utilities for sockets */ 
declare function useSocket (): {
    readonly socket: Ref<WebSocket | null>
    /** Gets the correct protocole for the socket ws or wss */
    getWebsocketProtocole (): string
    /** Retturns the correct root address for the socket e.g. ws://example.com/path */
    websocketRootAddress (path: string): string
    /** Creates a new websocket */
    createWebsocket (path: string, listeners: listenerOptions): void
    /** Send a message via the websocket */
    send (type: string, items: object): object
}

declare function useUtilities (): {
    /** Create a random string */
    getRandomString(k: number = 10): string
    /** Check if a list of items has null values */
    hasNull (items: []): boolean
    /** Adds an "id" attribute to each item in a list of items */
    indexElements (items: []): []
    /** From a list of items, get the incremented last "id" attribute */
    incrementLastId (items: object[]): number | null
    /** Read a user uploaded file */
    readFile (file: File): string
    /** Read multiple uploaded files */
    readMultipleFiles (files: FileList[]): string[]
    /** Read a video file */
    readVideoFile (files: FileList[]): string[]
    /** Get a video frame a image */
    getVideoFrame (video: HTMLVideoElement): string
    /** Truncate a given text by k-length */
    truncate (text: string, k?: number): string
    /** Truncate a string based on it's length */
    conditionalTruncate (text: string, limit: number, k: number): string
    /** Manage the items of a list of strings and/or numbers by adding or removing non-existing elements accordingly */
    listManager (items: any[], item: string | number): any[]
    /** Manage the items of a list of dictionnaries by adding or removing non-existing elements accordingly */
    dictionnaryListManager (items: object[], item: object, key: string): object[]
    /** Checks whether a dictionnary exists in a list based on the value of one of its keys */
    dictionnaryExists (items: object[], key: string, test: string): boolean
    /** Based on the ID attribute of an element on the page, scroll to that element */
    scrollToSection (elementId: string): void
    /** Capitalize the first letter of a string */
    capitalizeFirstLetter (value): string
    /** Capitalize the first letters of a string */
    capitalizeLetters (value): string
    /** Format a number as a percentage */
    formatAsPercentage (value: number, negative?: boolean): string
    /** Get the percentage of the current element that was scrolled */
    getVerticalScrollPercentage (el: HTMLElement): number
    /** Quickly sort a list of items */
    quickSort (items: [], ascending?: boolean): []
}
 
declare function useUrls(): {
    /** Reconcile a path to a root url */
    rebuildPath (path: string): string
    /** Reconcile a media path to a root backend media url. Useful for returning the full url of images, videos on the backend */
    mediaUrl (path: string): string
    /** Build an url for pagination on the backend */
    buildLimitOffset (url: string, limit?: number, offset?: number): string
    /** Returns page number as url parameters */
    getPageFromParams (url: string, page?: number): string
} 

/** Compasable for adding extra functionnalities to Vue */
export declare module index {
    return {
        useSocket,
        useUtilities,
        useUrls,
        loadView,
        loadLayout,
        loadComponent
    }
}
