Feature: End to End Test

  Scenario: Generate, save, and retrieve a generated image.
    Given A request is made to the /generate endpoint using text prompt
      """
      In the style of a Mission Impossible action movie. Make a realistic action scene where
      a kitten is attempting to navigate through a laser maze. There is a safe in the background.
      """
    Then I should recieve a response with encoded image data.
    And I will save that image using /save with the name
      """
      Kitten Mission Impastable
      """
    And I should be able to retrieve the images data using /images endpoint
#And I should be able to view the image in my browser.