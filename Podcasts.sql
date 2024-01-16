SELECT id,
title,
url,
format(len(trim(transcript)),'###,###'),
right(transcript,100)
FROM dbo.podcasts
WHERE len(trim(transcript)) < 10000
order by id asc


update dbo.podcasts
set title = 'S03E05: Tail Reaper'
where id = 23