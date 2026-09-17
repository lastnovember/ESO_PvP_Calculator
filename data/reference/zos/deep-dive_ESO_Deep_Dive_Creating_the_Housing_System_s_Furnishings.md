# ESO Deep Dive—Creating the Housing System’s Furnishings

Source: https://www.elderscrollsonline.com/en-us/news/post/62789
Tier: deep-dive
Published: unknown

Discover what goes into making all the things you can
 place in your home with this new Developer Deep Dive featuring members of ESO’s
 Systems team!
For our next Developer Deep Dive, we reached out to Senior
 Systems Designer Cullen Lee and Systems Designer Katrina Trotta to talk about
 how the team goes about adding furnishings to
ESO
’s robust Housing
 System.
Thank you both for taking the time to dive deep into
 furnishings! To get us started, what exactly is a furnishing item in ESO and
 how do players get them?
Cullen:
A furnishing is an item you can place in your home using the Housing
 System. There are many different types of furnishings, and with each update we
 try to release a variety of items using many of the lovely models that the Art
 teams were already creating for the zone.
We also create unique furnishings, too, like music boxes or
 some of our Crown Store offerings, that are often relatively complex. A furnishing
 might have unique visuals or some kind of special effects on it, or it might
 have unique functionality like crafting stations or the Armory.
Katrina:
Yeah, basically if it exists as a fixture in
 the game, we can make it a furnishing, and even if it doesn't exist as a
 fixture yet, we can request it.
When it comes to acquiring furnishings, players have many
 ways to get them in game. There's crafting, pickpocketing, looting, clickies,
 or the master writ and luxury vendors, just to name a few. We have our own
 special portion of the Crown Store that exists through the Housing Editor in
 addition to Crown Store bundles and limited-time offers. We have furnishings
 incorporated into the rewards for other systems like Achievements, Antiquities,
 or Tales of Tribute, as well.
Is it difficult to determine which items should be made
 into furnishings?
Cullen:
Yeah! With all the beautiful things that our
 artists create, we have an embarrassment of riches, so one of our main
 responsibilities is identifying which furnishings to generate. We want to make
 sure that, given the things that we know players will really want, the
 selection we land on hits those top desires within the time we have for the
 update.
But even before that, we have to figure out what kind of
 broad themes we want to hit with the update, what number of objects we want to
 make, and from what sources. For example, when working with the Tales of
 Tribute team, we decided early on that we wanted to have a certain number of Tribute
 furnishings that you could earn via achievements and by playing Tribute, so we
 budgeted that into our schedule.
Furnishings can be
 decorative, functional, or both
Does the ESO community play a role in the selection or
 even the design and creation of new furnishings?
Cullen:
They absolutely do! We have a big list of player-requested
 furnishings that we go back to periodically when we're looking for inspiration.
 And when we're picking out our new furnishings, we try to make sure that we're building
 off our learnings from the past in terms of what players were excited for and asked
 for in previous updates.
A good recent example of that is in the structural set that
 we've added as part of Update 35. It includes a transparent window that you can
 plug into doorways or more custom-built frames—it’s pretty flexible, and it
 provides a new tool for people who want to build a custom house from scratch
 and have windows that let you actually look outside. Items like that are a
 direct result of the feedback we get from the housing community.
Was that the case with the recently revealed Sacred Hourglass
 of Alkosh (a new item that allows you to change the time of day in your home)?
Cullen:
Yeah! That's based on some tech that we've
 wanted to develop for a long time, but which was actually prototyped by one of our
 engineers, Jimmy, whom the community may know as Cardinal05.
We hired him after he had created a super in-depth housing
 mod, so he is someone who started out in the community as a huge housing fan and
 has been an invaluable resource to the team.
So, what is the process from start to finish for the
 creation of a furnishing item?
Katrina:
Let’s use a music box as an example, since
 we build all of these from scratch. For a given update, we come up with several
 pitches for new music boxes, some of which get approved. Once we get the music box
 idea approved, we send references and descriptions of how we’d like it to look
 to the Concept Art team and inform the Audio team we’ve started.
Once concept is complete and approved (everything needs
 approval!) and sent out to the larger team, we’re always in awe of how they’ve
 brought our ideas to life. At that point, our Environment team sculpts it in 3D,
 and with that 3D model now in-hand, we as Housing Designers can set up all the
 data required to make it an item players can interact with. We’re not done at
 that stage, though, since it needs animation and, usually, visual effects and
 lighting as well, so we usually have to wait for those to come in from those
 teams before we can call this closer to done. The work that the Animation team
 does is applied directly to the 3D model, so there’s no need for us to
 interfere with it. The Visual Effects team needs the data that we’ve stood up
 for them to use as the backbone to apply their work to it as well.
We need our Editorial department to name it and describe it,
 and we also keep Audio looped in as well so Editorial and Audio are on the same
 page for the description of the melody. We get an icon for it from the Environment
 team and marketing art from the Media Art team. The most important part of
 this, the melody for the music box, usually comes in last, from the Audio team.
 Once QA looks over all portions of it, then we can call it done!
Custom-made
 furnishings take a village to craft
It sounds like it takes a village to create a new
 furnishing. How does the Systems team manage it all?
Katrina:
Most of the work related to how it looks
 happens outside of our team, but the Housing Design team does a lot of work and
 research on planning what to pull in as furnishings for a given update. We
 generally do at least 50 new furnishings per update, which is a lot of data to
 manage. We survey themes for the area, play the content to get an idea of what
 players will encounter, and coordinate with teams like In-Game Cosmetics and
 Content Design so that everything fits right.
While Housing Designers can’t commit new pieces of art to
 our build, we make it work by being the ones to request the parts to be built,
 then build the data for the items themselves and the data around it that gets
 it to the player. We decide what furnishings to make, where the players get
 them from, and how to craft them if they’re crafted—all the while making sure the
 experience engages players.
How is the process different when you're creating a furnishing
 from a pre-existing asset made for a new zone?
Katrina:
Working with one singular item whose
 geometry already exists needs its data hooked up, an icon created, and a
 player-facing name applied to it. We bypass the Concept and 3D Modeling request
 stages with these, so it’s a simpler process on an individual furnishing’s
 level. However, when we do these types of items, we do them in large groups, so
 it’s not a trivial process. We tend to go over carefully what we pick for what
 sourcing type, and get it approved before any data work begins.
Not every 3D asset in our game is immediately usable for
 housing. For performance reasons, some assets are "finished" only on
 the sides that are visible to the player. With housing, all sides are visible,
 and therefore sometimes extra work is needed on the asset to get it to a usable
 state.
At what point in the process do you introduce QA to the new item?
Katrina:
QA is part of the process the whole way.
 They review it when the 3D asset is completed, when the data is set up, and
 again at the end once it’s obtainable in game. We try to notify them at as many
 stages of development as we can.
You can find
 furnishings from many different locations.
Given the flexibility of the Housing Editor, how challenging
 is a new furnishing item for the QA team to test?
Cullen:
Generally speaking, QA already has a regular test
 plan that has a variety of different checks in it. They make sure that the
 previews work correctly, that the interacts work correctly, that everything
 sounds appropriate, et cetera. And then if something breaks unexpectedly, we
 add a check to that test plan so that we don't run into the problem again in
 the future. There's always a secondary check in our release candidate build
 before it goes out to players, too. The process definitely requires expertise,
 but this way we avoid having to overcome the same challenges from scratch every
 time.
The Housing System is very robust, and players like to utilize
 furnishings in all kinds of complex and creative ways. Is it possible to
 account for all the different ways our players can use furnishings?
Cullen:
We definitely try to think about how people
 are going to use a new item, and we always try to think a little bit outside
 the box. We're still consistently surprised by some of the creative stuff the
 players come up with, which is awesome.
I just saw a build where they decorated a plot with tiny
 miniature versions of houses that were made from things like jewelry boxes with
 parts of books clipped through to make tiny doors. Some lovely, totally off-the-wall
 usage I’ve never seen before with some of our more standard furnishings, and
 that's not something that we would have predicted.
When we're creating furnishings, we always try to make sure
 that they're as flexible as we can make them. In Update 35 for example, we
 added a new kind of nice tile floor with a bottom that looks like rafters in a
 ceiling. That way if you're building a house with it, you naturally get
 ceilings below and floors above. Or you can turn it on its side and use it to
 make little cubby holes to hold paintings.
We love when people are creative with furnishings, and we want
 to support it wherever we can.
Katrina:
Yeah, I think platforms are some of my
 favorite things to do, especially if the top is not the same as the bottom. I
 love seeing players use platforms in unusual ways. It’s great seeing people log
 in to get at the new furnishings, because they use things in ways that I never
 thought possible. The creative brain is fantastic, and it can't be predicted.
Even the most
 basic items can be used in unexpected ways
Do you have any shout outs to the ESO Housing community
 that you’d like to make?
Cullen:
I don't want to single any individual out because I don't want
 to forget anyone, but the people who post their homes on Reddit and the forums,
 and whose who share them in various housing guilds’ contests and with friends
 are what makes this community thrive. They show off what is possible and are a huge
 part of why housing is as fun as it is. The system would not be nearly as cool without
 y’all doing these amazing things.
Katrina:
We also really appreciate the YouTubers and
 streamers. It’s really nice to get immediate feedback on an item. We often pull
 up a stream or look at a video someone recorded in the first week of PTS and see
 immediate feedback on what they liked and what they didn't like, and that can
 be a tremendous morale boost. And of course, seeing our players care a lot
 about what we care a lot about can help us make better decisions in the future,
 or get fixes in sooner rather than later.
A big thank you to both Katrina and Cullen for taking the
 time to dive deep into the Housing Systems’ furnishings. With more and more
 items being added to the pool each update, we love seeing how the community
 uses them to create ever-more incredible builds, so keep them coming! If you
 enjoyed this deep dive, tell us which furnishing you make the most creative use
 out of when working on your homes via
Twitter
,
Instagram
, and
Facebook
!
Development
