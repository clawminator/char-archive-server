import {createStore} from 'vuex'

export default createStore({
    state: {
        siteAlerts: [],
        showStatus: [],
        showSpinner: false,
        showFolderModal: false,
        showSearchModal: false,
        searchResults: {},
        searchQuery: "",
        sharedCurrentPath: null,
        sharedCurrentPathData: {},
        sharedCurrentPage: 1,
        scrollToDataPath: null,
        siteDisabled: false,
        showLoadingPlaceholder: false,
        sharedSiteLockMsg: null,
        archiveIs404: false,
        archiveIs500: false,
        archiveIs429: false,
        cardData: {},
        cardType: "",
        cardAuthorStr: "",
        cardSource: "",
        authorData: {},
        searchKeys: {},
    }, mutations: {
        addAlert(state, payload) {
            if (!state.siteAlerts.includes(payload)) {
                state.siteAlerts.push(payload);
            }
        }, removeAlert(state, index) {
            state.siteAlerts.splice(index, 1);
        }, clearAlerts(state) {
            state.siteAlerts = [];
        }, addStatus(state, payload) {
            // Don't allow duplicate statuses.
            if (!state.showStatus.includes(payload)) {
                state.showStatus.push(payload);
            }
        }, removeStatus(state, index) {
            state.showStatus.splice(index, 1);
        }, clearStatus(state) {
            state.showStatus = [];
        }, showSpinner(state, payload) {
            state.showSpinner = payload
        }, setFolderModalVisibility(state, payload) {
            state.showFolderModal = payload
        }, showSearchModal(state, payload) {
            state.showSearchModal = payload
        }, searchResults(state, payload) {
            state.searchResults = payload
        }, searchQuery(state, payload) {
            state.searchQuery = payload
        }, sharedCurrentPath(state, payload) {
            state.sharedCurrentPath = payload
        }, scrollToDataPath(state, payload) {
            state.scrollToDataPath = payload
        }, siteDisabled(state, payload) {
            state.siteDisabled = payload
        }, showLoadingPlaceholder(state, payload) {
            state.showLoadingPlaceholder = payload
        }, sharedCurrentPage(state, payload) {
            state.sharedCurrentPage = payload
        }, sharedCurrentPathData(state, payload) {
            state.sharedCurrentPathData = payload
        }, sharedSiteLockMsg(state, payload) {
            state.sharedSiteLockMsg = payload
        }, archiveIs404(state, payload) {
            state.archiveIs404 = payload
        }, cardData(state, payload) {
            state.cardData = payload
        }, cardType(state, payload) {
            state.cardType = payload
        }, cardAuthorStr(state, payload) {
            state.cardAuthorStr = payload
        }, cardSource(state, payload) {
            state.cardSource = payload
        }, authorData(state, payload) {
            state.authorData = payload
        }, archiveIs500(state, payload) {
            state.archiveIs500 = payload
        }, archiveIs429(state, payload) {
            state.archiveIs429 = payload
        }, searchKeys(state, payload) {
            state.searchKeys = payload
        }
    }, getters: {
        alertExists: (state) => (message) => {
            return state.siteAlerts.includes(message);
        }, statusExists: (state) => (message) => {
            return state.showStatus.includes(message);
        },
    }
})
