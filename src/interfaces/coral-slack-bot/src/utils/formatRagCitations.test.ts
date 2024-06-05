import { describe, expect, test } from 'vitest';

import { formatRagCitations } from './formatRagCitations';

describe('formatRagCitations', () => {
  test('format RAG response into a list of bullet points, each as a slack link using the citation title + url', () => {
    const chatResponse = {
      response_id: 'aef874ef-bc61-45aa-9ade-4efac4fb12d3',
      conversation_id: '1705939582_599929-C05M1US4SSX',
      text: "Here are some hotels in San Francisco:\n\n- Le Méridien San Francisco\n- Hilton San Francisco Financial District\n\nI'm also able to provide you with corporate rates at these hotels. Who are you booking on behalf of?",
      generation_id: '2873a17a-30db-4d7d-a60a-d58cc7daa366',
      citations: [
        {
          start: 42,
          end: 67,
          text: 'Le Méridien San Francisco',
          document_ids: ['elastic-search-slack-v1-0bdrwb_1', 'elastic-search-slack-v1-0bdrwb_3'],
        },
        {
          start: 70,
          end: 109,
          text: 'Hilton San Francisco Financial District',
          document_ids: ['elastic-search-slack-v1-0bdrwb_1', 'elastic-search-slack-v1-0bdrwb_0'],
        },
      ],
      documents: [
        {
          document_id: 'elastic-search-slack-v1-0bdrwb_1',
          snippet:
            "Hi Jason! We don't yet have a corporate rate set up at a San Francisco hotel but we're working on it. Here are two hotels I recommend near the new office: • *<https://www.hilton.com/en/hotels/sfofdhf-hilton-san-francisco-financial-district/|Hilton San Francisco Financial District>*750 Kearny St. San Francisco (0.4 mi / 10 min walk) • *<https://www.marriott.com/en-us/hotels/sfomd-le-meridien-san-francisco/overview/|Le Méridien San Francisco>*333 Battery St, San Francisco, CA 94111",
          title: 'Corporate rate',
          url: 'https://cohereai.slack.com/archives/ask-people/p1699027927.191979?thread_ts=1699026229.534229',
          text: '',
        },
        {
          document_id: 'elastic-search-slack-v1-0bdrwb_3',
          snippet:
            'For SF, we have a corp rate at <https://www.marriott.com/en-us/hotels/sfomd-le-meridien-san-francisco/overview/|Le Meridien Hotel> - you can book through melon or by contacting the hotel!',
          title: 'Le Meridien Hotel',
          url: 'https://cohereai.slack.com/archives/ask-people/p1698415906.928069?thread_ts=1698354798.078099',
          text: '',
        },
      ],
      is_finished: true,
      finish_reason: '',
      chat_history: [],
    };
    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(`
*Sources:*
- <https://cohereai.slack.com/archives/ask-people/p1699027927.191979?thread_ts=1699026229.534229|Corporate rate>
- <https://cohereai.slack.com/archives/ask-people/p1698415906.928069?thread_ts=1698354798.078099|Le Meridien Hotel>`);
  });

  test('combine duplicate RAG response links into one citation and exclude documents that are not cited', () => {
    const chatResponse = {
      response_id: 'eda5a86b-3821-4b34-bac5-19ed784a65c5',
      conversation_id: '1705940745_274189-C05M1US4SSX',
      text: "Here are some hotels you can book in Toronto:\n\n- The Westin Harbour Castle Hotel\n- The Ace Hotel (51 Camden Street)\n- The Hilton Toronto (145 Richmond Street West)\n\nI'm unsure if these hotels have a corporate rate with Cohere. Do you want me to make a reservation at any of these hotels?",
      generation_id: 'e0de1fc1-997c-44c2-a61a-7900fe6e38d2',
      citations: [
        {
          start: 83,
          end: 96,
          text: 'The Ace Hotel',
          document_ids: ['elastic-search-notion-v1-qwq4cr_0:0'],
        },
        {
          start: 98,
          end: 114,
          text: '51 Camden Street',
          document_ids: ['elastic-search-notion-v1-qwq4cr_0:0'],
        },
        {
          start: 118,
          end: 136,
          text: 'The Hilton Toronto',
          document_ids: ['elastic-search-notion-v1-qwq4cr_0:1'],
        },
        {
          start: 138,
          end: 162,
          text: '145 Richmond Street West',
          document_ids: ['elastic-search-notion-v1-qwq4cr_0:1'],
        },
        {
          start: 199,
          end: 213,
          text: 'corporate rate',
          document_ids: [
            'elastic-search-notion-v1-qwq4cr_0:0',
            'elastic-search-notion-v1-qwq4cr_0:1',
          ],
        },
        {
          start: 219,
          end: 226,
          text: 'Cohere.',
          document_ids: [
            'elastic-search-notion-v1-qwq4cr_0:0',
            'elastic-search-notion-v1-qwq4cr_0:1',
          ],
        },
      ],
      documents: [
        {
          document_id: 'elastic-search-notion-v1-qwq4cr_4',
          snippet:
            'ACL in Toronto\nOrganizers: Isabelle Camp, Kristina\nDate: July 9, 2023 → July 14, 2023\nSponsorship Details: ACL Overview (ACL%20in%20Toronto%20cc43474578504fd08f613954aef2a164/ACL%20Overview%208ec7a7a34db34f9f9138433a82b5b495.md) \nTags: Conference\nLocation: Westin Harbour Castle Hotel, Toronto\nACL Overview\nACL Overview (1)',
          title: 'ACL in Toronto',
          url: 'https://notion.com/cc43474578504fd08f613954aef2a164',
          text: '',
        },
        {
          document_id: 'elastic-search-notion-v1-qwq4cr_0:0',
          snippet:
            'Toronto Hotels\nWe now have a Co:here Corporate Rate for The Ace Hotel or The Hilton Toronto!\n🏨 The Ace Hotel - 51 Camden Street\n\nURL Booking Link: Any time you need to make a reservation at The Ace Hotel, you will simple click this link to take you directly to the hotel site and it will have Cohere’s negotiated rates all populated: Ace Toronto Cohere Reservations\nYou can also book through their website directly and use the promotional code: COHERE\nReservation Department \nYou can either email reservations.tor@acehotel.com or call 416.637.1200. Please mention the corporate code: COHERE. \nDirections from Ace Hotel to Toronto Office \nIs a 10 minute walk to the office, or a 5 minute car ride.',
          title: 'Toronto Hotels',
          url: 'https://notion.com/36d91c8bcf79464388f45f577675bed8',
          text: '',
        },
        {
          document_id: 'elastic-search-notion-v1-qwq4cr_0:1',
          snippet:
            ' \nhttps://goo.gl/maps/feSQpnv5MTgvSEUK6\n🏨 The Hilton - 145 Richmond Street West\n\nURL Booking Link:  Any time you need to make a reservation at The Hilton Toronto Hotel, you will simply click this link to take you directly to the hotel site and it will have Cohere’s negotiated rates all populated.\nhttps://www.hilton.com/en/book/reservation/rooms/?ctyhocn=TORHIHH&corporateCode=3357341\nReservations Department\nCall + 1-800-HILTONS or 1-800-445-8667 Reservations department\nAsk for the COHERE AI Corporate rate or mention the Corporate Account number 3357341\nHilton Honors App\nSearch for Hilton Toronto\nEnter your Check-in/out dates\nUnder Special Rates enter 3357341, and hit Apply.\n',
          title: 'Toronto Hotels',
          url: 'https://notion.com/36d91c8bcf79464388f45f577675bed8',
          text: '',
        },
      ],
      finish_reason: '',
      is_finished: true,
      chat_history: [],
    };

    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(`
*Sources:*
- <https://notion.com/36d91c8bcf79464388f45f577675bed8|Toronto Hotels>`);
  });

  test('safely handles RAG response with not citation', () => {
    const chatResponse = {
      response_id: 'eda5a86b-3821-4b34-bac5-19ed784a65c5',
      conversation_id: '1705940745_274189-C05M1US4SSX',
      text: 'I could not find any information.',
      generation_id: 'e0de1fc1-997c-44c2-a61a-7900fe6e38d2',
      is_finished: true,
      finish_reason: '',
      chat_history: [],
    };

    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(``);
  });
});
