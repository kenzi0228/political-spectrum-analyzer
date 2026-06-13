# Advertising and privacy deployment

## Implemented in the application

- the AdSense publisher meta tag and `ads.txt` declaration;
- no AdSense network script before an explicit advertising choice;
- refusal leaves every analysis feature available;
- permanent links to privacy, legal, and advertising choices;
- reserved styling for third-party ad surfaces to limit layout shift;
- a Content Security Policy restricted to the required Google advertising
  origins.

## Required account configuration

For visitors in the EEA, United Kingdom, and Switzerland, configure a
Google-certified consent management platform in AdSense Privacy & messaging
before enabling personalized advertising.

The in-app choice records whether the site may load AdSense. It is not presented
as a substitute for Google CMP certification.

## Placement policy

Advertising must not:

- appear inside score controls, analysis conclusions, or the political map;
- resemble navigation, filters, or download buttons;
- obscure legal or methodology content;
- cause content to move after interaction;
- be loaded when advertising consent is rejected.

Prefer one reserved placement after substantive editorial content. Do not add a
manual AdSense unit until its real `data-ad-slot` identifier exists; placeholder
unit IDs must never be committed.
