POLICY_NO_REFERRER = 'no-referrer'

POLICY_NO_REFERRER_WHEN_DOWNGRADE = 'no-referrer-when-downgrade'

POLICY_SAME_ORIGIN = 'same-origin'

POLICY_ORIGIN = 'origin'

POLICY_STRICT_ORIGIN = 'strict-origin'

POLICY_ORIGIN_WHEN_CROSS_ORIGIN = 'origin-when-cross-origin'

POLICY_STRICT_ORIGIN_WHEN_CROSS_ORIGIN = 'strict-origin-when-cross-origin'

POLICY_UNSAFE_URL = 'unsafe-url'

POLICY_ZINEB_DEFAULT = 'zineb-default'

POLICY_REFERRERS = {
    'no-referrer', 'no-referrer-when-downgrade', 'same-origin',
        'origin', 'strict-origin', 'origin-when-cross-origin',
            'strict-origin-when-cross-origin', 'unsafe-url', 'zineb-default'
}


class Policy:
    def referer(self, request_url, response_url):
        pass


class NoReferer(Policy):
    pass


class NoRefererWhenDowngrade(Policy):
    pass


class SameOrigin(Policy):
    pass


class Origin(Policy):
    pass


class Referer:
    def __call__(self, sender, **kwargs):
        print('Referer', sender)

        url = kwargs.get('url')

        policy_klass = Policy()
        policy = kwargs.get('referrer')
        if policy in POLICY_REFERRERS:
            policy_klass.referer(url, '')
