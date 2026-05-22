# Reference dataset profile audit

## Summary

- Profiles: 500
- Gender values: {'female': 148, 'male': 352}
- Confidence values: {'high': 23, 'low': 70, 'medium': 407}
- Role categories: 16
- Gender corrections applied: 174
- Coordinate overrides applied: 13
- Coordinate rows flagged for manual review: 7

## Gender correction policy

Gender is normalized to `male` / `female` only for known public or historical people when the correction is high-confidence.
The script does not silently keep `unknown`: unresolved cases abort the patch so they can be reviewed instead of guessed.

## Coordinate correction policy

This commit applies only a short list of high-confidence coordinate overrides.
The remaining questionable placements are exported to `data/reference/profile_coordinate_audit.csv` for explicit review.

## Applied coordinate overrides

| Name | Old x | Old y | New x | New y | Rationale |
|---|---:|---:|---:|---:|---|
| Friedrich Hayek | 2.2 | -1.2 | 2.8 | -1.3 | Classical liberal / Austrian economics placement should be more economically right-libertarian. |
| Machiavelli | 1.5 | 2.1 | 0.7 | 1.8 | Political realism is not strongly market-right; authoritarian/order dimension remains high. |
| Hannah Arendt | 0.2 | 0.4 | 0.1 | -0.7 | Republican anti-totalitarian pluralism is more anti-authoritarian than the previous y=0.4 placement. |
| Robert Nozick | 2.8 | -1.9 | 3.3 | -2.3 | Libertarian political theory should be more explicitly right-libertarian. |
| Murray Rothbard | 3.6 | -3.0 | 3.8 | -3.4 | Anarcho-capitalist theory should be near the right-libertarian extreme. |
| Barack Obama | 0.5 | -0.1 | 0.4 | -0.6 | Mainstream social liberalism is more socially liberal than the earlier near-neutral y. |
| Xi Jinping | -1.2 | 3.0 | 0.0 | 3.2 | Contemporary Chinese governance is strongly authoritarian; economic placement is statist/mixed rather than classic far-left. |
| Deng Xiaoping | 0.2 | 2.0 | 1.0 | 2.4 | Market reforms and authoritarian party-state governance make the earlier x=0.2 too economically centrist-left. |
| Lee Kuan Yew | 1.5 | 2.0 | 1.8 | 2.4 | Developmental market governance plus strong state authority warrants a clearer right-authoritarian placement. |
| King Faisal | 1.5 | 2.9 | 1.6 | 3.0 | Conservative monarchy should remain strongly authoritarian. |
| Mohammed bin Salman | 2.0 | 2.5 | 2.3 | 2.8 | Authoritarian monarchy with reformist market-development orientation should sit higher and further right. |
| Aung San Suu Kyi | 0.2 | -1.4 | 0.2 | -0.2 | Pro-democracy dissident image and later governing record require a less libertarian y placement. |
| Marine Le Pen | 0.2 | 2.1 | 1.0 | 2.8 | National populism, sovereignty politics, and immigration restriction warrant a clearer right-authoritarian placement. |

## Top rows requiring later manual coordinate review

| Name | Family | Role | x | y | Flags |
|---|---|---|---:|---:|---|
| Thomas Hobbes | Authoritarianism | Thinker | 1.0 | 1.7 | authoritarianism with y < 2.0 |
| Augusto Pinochet | Liberalism | Authoritarian ruler | 3.2 | 1.6 | authoritarian ruler with y < 2.0 |
| Murray Rothbard | Anarchism | Economist | 3.8 | -3.4 | left/social anarchism with x > 0.5 |
| Josip Broz Tito | Other | Authoritarian ruler | -1.3 | 1.5 | authoritarian ruler with y < 2.0 |
| Woodrow Wilson | Progressivism | Head of state | 0.4 | 1.2 | progressivism with y > -0.5 |
| Deng Xiaoping | Socialism | Political Leader | 1.0 | 2.4 | socialism with x > 0.2 |
| Kim Il-sung | Communism | Authoritarian ruler | -2.8 | 3.9 | near graph boundary; verify that extremity is intentional |
