-- Point all simulation challenges at the FindBug Academy branded lab.
-- Port 5050 only — never 3000 (frontend) or 8080 (legacy WebGoat).
UPDATE simulation_challenges
SET
  docker_image = 'findbug/academy-lab',
  exposed_port = 5050
WHERE docker_image IN (
  'bkimminich/juice-shop',
  'webgoat/webgoat-8.0',
  'findbug/academy-lab'
)
OR docker_image IS NULL
OR exposed_port IN (3000, 8080, 80);
