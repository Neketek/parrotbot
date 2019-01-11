INSERT INTO subscriber
(
  id,
  name,
  display_name,
  admin,
  bot_admin,
  tz,
  active,
  archived
)
VALUES
(
  "FID:1",
  "f:name:1",
  "f:dname:1",
  1,
  0,
  "UTC",
  1,
  0
),
(
  "FID:2",
  "f:name:2",
  "f:dname:2",
  1,
  0,
  "UTC",
  1,
  0
),
(
  "FID:3",
  "f:name:3",
  "f:dname:3",
  1,
  0,
  "UTC",
  1,
  0
);

SELECT
  s.id as id,
  (count(r.id) = 0) as 'delete'
FROM subscriber as s
LEFT JOIN subscription as ss
ON ss.subscriber_id = s.id
LEFT JOIN report as r
ON r.subscription_id = ss.id
GROUP BY s.id;


INSERT INTO report
(
  created,
  expiration,
  completed,
  subscription_id
)
VALUES
(
  datetime(),
  datetime(),
  datetime(),
  1
);
